import heapq
import math

from panda3d.core import (BitMask32, CollisionBox, CollisionHandlerQueue,
                         CollisionNode, CollisionRay, CollisionSegment,
                         CollisionSphere, CollisionTraverser, NodePath, Point3)

from toontown.strike.StrikeBarricades import BARRICADES
from toontown.toonbase import ToontownGlobals


class StrikeNavigationAI:
    spacing = 4.0
    clearance = 1.25

    def __init__(self, source):
        self.root = NodePath('strike-navigation')
        self.geom = source.copyTo(self.root)
        self.traverser = CollisionTraverser('strike-navigation')
        self.queue = CollisionHandlerQueue()
        self.probe = self.root.attachNewNode(CollisionNode('navigation-probe'))
        self.probe.node().setIntoCollideMask(BitMask32.allOff())
        self.traverser.addCollider(self.probe, self.queue)
        self.cells = {}
        self.edges = {}
        self.barrierRoot = self.root.attachNewNode('locked-barricades')
        self.blockers = []
        self.revision = 0
        for barricade in BARRICADES:
            blocker = self.barrierRoot.attachNewNode(CollisionNode('navigation-barricade'))
            blocker.node().setIntoCollideMask(ToontownGlobals.WallBitmask)
            blocker.node().setFromCollideMask(BitMask32.allOff())
            for pattern in barricade.get('collisionNodes', ()):
                target = self.geom.find(pattern)
                if not target.isEmpty():
                    bounds = target.getTightBounds(self.root)
                    if bounds:
                        padding = Point3(0.5, 0.5, 0.2)
                        blocker.node().addSolid(CollisionBox(bounds[0] - padding,
                                                            bounds[1] + padding))
            if 'blocker' in barricade:
                x, y, z, heading, width, depth, height = barricade['blocker']
                blocker.setPosHpr(x, y, z, heading, 0, 0)
                blocker.node().addSolid(CollisionBox(Point3(-width / 2, -depth / 2, 0),
                                                    Point3(width / 2, depth / 2, height)))
            self.blockers.append(blocker)

    def unlock(self, index):
        self.blockers[index].removeNode()
        for pattern in BARRICADES[index]['nodes']:
            for node in self.geom.findAllMatches(pattern):
                node.removeNode()
        self.cells.clear()
        self.edges.clear()
        self.revision += 1

    def query(self, mask, solids, root=None):
        node = self.probe.node()
        node.clearSolids()
        node.setFromCollideMask(mask)
        for solid in solids:
            node.addSolid(solid)
        self.queue.clearEntries()
        self.traverser.traverse(self.root if root is None else root)
        return self.queue.getNumEntries()

    def floor(self, x, y):
        self.query(ToontownGlobals.FloorBitmask,
                   [CollisionRay(x, y, 1000, 0, 0, -1)])
        heights = [self.queue.getEntry(i).getSurfacePoint(self.root).z
                   for i in range(self.queue.getNumEntries())]
        heights = [z for z in heights if -20 <= z <= 30]
        return Point3(x, y, min(heights)) if heights else None

    def standable(self, point):
        return not self.query(ToontownGlobals.WallBitmask,
                              [CollisionSphere(point + Point3(0, 0, 2), self.clearance)])

    def segment(self, start, end):
        delta = end - start
        length = math.hypot(delta.x, delta.y)
        if length < 0.001:
            return abs(delta.z) <= 3
        side = Point3(-delta.y / length, delta.x / length, 0) * self.clearance
        lift = Point3(0, 0, 2)
        solids = [CollisionSegment(start + lift + side * offset,
                                   end + lift + side * offset)
                  for offset in (-1, 0, 1)]
        if self.query(ToontownGlobals.WallBitmask, solids):
            return False
        previous = start
        count = max(1, math.ceil(length / 2))
        for step in range(1, count + 1):
            point = start + delta * (step / count)
            ground = self.floor(point.x, point.y)
            if ground is None or abs(ground.z - previous.z) > 3:
                return False
            previous = ground
        return abs(previous.z - end.z) <= 3

    def cell(self, key):
        if key not in self.cells:
            x, y = key[0] * self.spacing, key[1] * self.spacing
            point = self.floor(x, y) if max(abs(x), abs(y)) <= 300 else None
            self.cells[key] = point if point is not None and self.standable(point) else None
        return self.cells[key]

    def anchors(self, point):
        gx, gy = round(point.x / self.spacing), round(point.y / self.spacing)
        candidates = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                key = gx + dx, gy + dy
                cell = self.cell(key)
                if cell is not None:
                    candidates.append(((cell - point).lengthSquared(), key, cell))
        return [(key, cell) for _, key, cell in sorted(candidates)
                if self.segment(point, cell)][:4]

    def route(self, start, goal):
        if self.segment(start, goal):
            return [Point3(goal)]
        starts, goals = self.anchors(start), dict(self.anchors(goal))
        if not starts or not goals:
            return []
        frontier, costs, parents = [], {}, {}
        for key, point in starts:
            costs[key] = (point - start).length()
            parents[key] = None
            heapq.heappush(frontier, (costs[key] + (point - goal).length(), key))
        visited = set()
        while frontier and len(visited) < 2500:
            _, key = heapq.heappop(frontier)
            if key in visited:
                continue
            if key in goals:
                path = [Point3(goal)]
                while key is not None:
                    path.append(Point3(self.cell(key)))
                    key = parents[key]
                path.reverse()
                result, origin = [], start
                for index in range(1, len(path)):
                    if not self.segment(origin, path[index]):
                        result.append(path[index - 1])
                        origin = path[index - 1]
                result.append(Point3(goal))
                return result
            visited.add(key)
            point = self.cell(key)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)):
                other = key[0] + dx, key[1] + dy
                candidate = self.cell(other)
                if candidate is None or other in visited:
                    continue
                edge = tuple(sorted((key, other)))
                if edge not in self.edges:
                    self.edges[edge] = self.segment(point, candidate)
                if not self.edges[edge]:
                    continue
                cost = costs[key] + (candidate - point).length()
                if cost < costs.get(other, float('inf')):
                    costs[other], parents[other] = cost, key
                    heapq.heappush(frontier, (cost + (candidate - goal).length(), other))
        return []

    def landing(self, start, goal):
        angle = math.atan2(start.y - goal.y, start.x - goal.x)
        for radius in (18, 14, 10):
            for rotation in (0, 0.5, -0.5, 1, -1, 2, -2, math.pi):
                point = self.floor(goal.x + math.cos(angle + rotation) * radius,
                                   goal.y + math.sin(angle + rotation) * radius)
                if (point is not None and self.standable(point) and
                        self.segment(point, goal) and not self.query(
                            ToontownGlobals.WallBitmask,
                            [CollisionSegment(start + Point3(0, 0, 2),
                                              point + Point3(0, 0, 2))],
                            self.barrierRoot)):
                    return point
        return None

    def destroy(self):
        self.root.removeNode()
