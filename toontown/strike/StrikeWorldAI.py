from panda3d.core import NodePath
from toontown.strike.OSTZCalculatorAI import OSTZCalculatorAI
from toontown.strike.StrikeNavigationAI import StrikeNavigationAI


class StrikeWorldAI:
    def __init__(self, strike):
        self.strike = strike

        self.world = NodePath('strike-world-node-%s' % id(self))
        self.enemies = []
        self.navigation = None
        self.taskName = 'strike-movement-%s' % id(self)

    def addEnemy(self, enemy):
        en = NodePath('enemy-%s' % id(self))
        en.reparentTo(self.world)

        enemy.node = en

        self.enemies.append(enemy)

    def removeEnemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        enemy.route = []
        if enemy.node is not None:
            enemy.node.removeNode()
            enemy.node = None

    def registerParticipant(self, participant):
        pn = NodePath('participant-%s' % id(self))
        pn.reparentTo(self.world)

        participant.registerFlock(pn, None)

    def start(self):
        if self.navigation is None:
            self.navigation = StrikeNavigationAI(OSTZCalculatorAI.INSTANCE.geom)
            for index in range(2):
                if self.strike.barricadeMask & (1 << index):
                    self.navigation.unlock(index)
        taskMgr.add(self.update, self.taskName)

    def update(self, task):
        dt = min(globalClock.getDt(), 0.1)
        for enemy in self.enemies[:]:
            enemy.updateMovement(dt)
        return task.cont

    def destroy(self):
        taskMgr.remove(self.taskName)
        for enemy in self.enemies[:]:
            self.removeEnemy(enemy)
        if self.navigation:
            self.navigation.destroy()
        self.world.removeNode()
