from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from panda3d.core import Point3

from toontown.strike import CorporateStrikeGlobals

import time
import math


class DistributedStrikeEnemyAI(DistributedObjectAI):
    POS_BROADCAST_INTERVAL = 0.2

    def __init__(self, air, roundManager, type):
        DistributedObjectAI.__init__(self, air)

        self.roundManager = roundManager
        self.strike = roundManager.strike

        self.type = type
        self.initialPos = None

        self.node = None

        self.target = None
        self.dead = False
        self.lastHitByAvatar = {}
        self.lastAttack = 0.0
        self.level = self.roundManager.round
        self.maxHp = CorporateStrikeGlobals.getCogHp(self.level)
        self.hp = self.maxHp
        self.lastFlight = 0.0
        self.flightComplete = 0.0
        self.movementState = 'spawning'
        self.route = []
        self.routeGoal = None
        self.nextRouteTime = 0.0
        self.lastRecoveryGoal = None
        self.failedSince = None
        self.nextBroadcast = 0.0
        self.walkSpeed = 7.0

    def getType(self):
        return self.type

    def getHp(self):
        return self.hp

    def getMaxHp(self):
        return self.maxHp

    def getLevel(self):
        return self.level

    def setInitialPos(self, x, y, z, h):
        self.initialPos = (x, y, z, h)

    def getInitialPos(self):
        return self.initialPos

    def setNodePosition(self, x, y, h, z=0.0):
        self.node.setX(x)
        self.node.setY(y)
        self.node.setZ(z)
        self.node.setH(h)

    def targetParticipant(self, participant):
        if self.dead:
            return
        if self.target is not participant:
            self.route = []
            self.nextRouteTime = 0.0
        self.target = participant

    def recoverPath(self):
        self.route = []
        self.routeGoal = None
        self.nextRouteTime = 0.0
        self.lastRecoveryGoal = None

    def updateMovement(self, dt):
        if self.dead or self.node is None or self.movementState == 'spawning':
            return
        now = time.time()
        if self.movementState == 'flying':
            if now < self.flightComplete:
                return
            self.movementState = 'walking'
            self.failedSince = None
            self.nextRouteTime = 0.0
        living = [p for p in self.strike.participants
                  if p.node is not None and p.hp > 0 and not p.hasPowerup('disguise')]
        if not living:
            self.target = None
            self.route = []
            return
        participant = min(living, key=lambda p: self.distanceTo(p))
        self.targetParticipant(participant)
        navigation = self.strike.world.navigation
        goal = navigation.floor(participant.node.getX(), participant.node.getY())
        if goal is None:
            return
        position = self.node.getPos()
        if self.distanceTo(participant) <= 4.5 and navigation.segment(position, goal):
            self.node.headsUp(goal)
            self.route = []
            self.failedSince = None
        else:
            moved = self.routeGoal is None or (goal - self.routeGoal).length() > 3
            if now >= self.nextRouteTime and (moved or not self.route):
                self.route = navigation.route(position, goal)
                self.routeGoal = Point3(goal)
                self.nextRouteTime = now + (0.75 if self.route else 2.0)
            if self.route:
                self.failedSince = None
                destination = self.route[0]
                delta = destination - position
                distance = delta.length()
                if distance <= self.walkSpeed * dt:
                    self.node.setPos(destination)
                    self.route.pop(0)
                else:
                    self.node.setPos(position + delta * (self.walkSpeed * dt / distance))
                ground = navigation.floor(self.node.getX(), self.node.getY())
                if ground is not None:
                    self.node.setZ(ground.z)
                if math.hypot(delta.x, delta.y) > 0.01:
                    self.node.setH(math.degrees(math.atan2(-delta.x, delta.y)))
            elif self.failedSince is None:
                self.failedSince = now
            if ((self.failedSince is not None and now - self.failedSince > 4) or
                    self.distanceTo(participant) >= CorporateStrikeGlobals.ENEMY_FLIGHT_DISTANCE):
                self.flyToParticipant(participant)
        if now >= self.nextBroadcast:
            self.broadcastPos()
            self.nextBroadcast = now + self.POS_BROADCAST_INTERVAL

    def flyToParticipant(self, participant):
        if (self.dead or self.node is None or participant is None or participant.node is None or
                self.movementState != 'walking'):
            return
        now = time.time()
        if now - self.lastFlight < 15:
            return
        navigation = self.strike.world.navigation
        goal = navigation.floor(participant.node.getX(), participant.node.getY())
        if goal is None:
            return
        if self.lastRecoveryGoal is not None and (goal - self.lastRecoveryGoal).length() < 12:
            return
        landing = navigation.landing(self.node.getPos(), goal)
        self.lastFlight = now
        self.lastRecoveryGoal = Point3(goal)
        if landing is None:
            return
        self.route = []
        self.routeGoal = None
        self.movementState = 'flying'
        self.flightComplete = now + 1.75
        self.node.setPos(landing)
        self.node.headsUp(goal)
        self.sendUpdate('flyTo', [landing.x, landing.y, landing.z, self.node.getH()])

    def distanceTo(self, participant):
        delta = participant.node.getPos() - self.node.getPos()
        return math.hypot(delta.x, delta.y)

    def startPosBroadcast(self):
        self.movementState = 'walking'
        self.broadcastPos()

    def requestHit(self, gagType, power):
        if self.dead or gagType not in CorporateStrikeGlobals.GAGS:
            return
        if power < 0 or power > 100:
            return

        avId = self.air.getAvatarIdFromSender()
        participant = next((p for p in self.strike.participants if p.avId == avId), None)
        if participant is None or participant.node is None or self.node is None:
            return

        gag = CorporateStrikeGlobals.GAGS[gagType]
        now = time.time()
        if now - self.lastHitByAvatar.get(avId, 0.0) < gag['cooldown']:
            return

        distance = (participant.node.getPos() - self.node.getPos()).length()
        if distance > CorporateStrikeGlobals.getGagRange(gagType, power):
            return

        navigation = self.strike.world.navigation
        if navigation:
            start = navigation.floor(participant.node.getX(), participant.node.getY())
            end = navigation.floor(self.node.getX(), self.node.getY())
            if start is None or end is None or not navigation.segment(start, end):
                return
            direction = end - start
            direction.z = 0
            if direction.lengthSquared() > 0:
                direction.normalize()
                heading = math.radians(participant.node.getH())
                forward = Point3(-math.sin(heading), math.cos(heading), 0)
                if forward.dot(direction) < 0.25:
                    return

        if not participant.consumeAmmo(gagType):
            return

        self.lastHitByAvatar[avId] = now
        damage = gag['damage']
        if participant.hasPowerup('hyperbust'):
            damage = self.hp
        self.hp = max(0, self.hp - damage)
        participant.addPoints(CorporateStrikeGlobals.POINTS_PER_HIT)
        self.sendUpdate('hit', [avId, gagType, damage])
        taskMgr.doMethodLater(0.3, self.__broadcastHp,
                              self.uniqueName('strike-hit-hp'))
        if self.hp == 0:
            participant.addPoints(CorporateStrikeGlobals.POINTS_PER_KILL)
            self.dead = True
            self.roundManager.enemyDefeated(self)

    def __broadcastHp(self, task):
        self.sendUpdate('setHp', [self.hp])
        return task.done

    def canAttack(self):
        now = time.time()
        if (self.dead or self.movementState != 'walking' or
                now - self.lastAttack < CorporateStrikeGlobals.ENEMY_ATTACK_COOLDOWN):
            return False
        return True

    def emp(self):
        if self.dead:
            return
        self.dead = True
        self.hp = 0
        self.sendUpdate('hit', [0, 0, self.maxHp])
        self.roundManager.enemyDefeated(self)

    def broadcastPos(self):
        if self.dead or self.node is None or self.movementState != 'walking':
            return
        pos = self.node.getPos()
        h = self.node.getH()
        self.sendUpdate('setPosition', [pos.x, pos.y, pos.z, h,
                                       globalClockDelta.getRealNetworkTime(bits=16)])
