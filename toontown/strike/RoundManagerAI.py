from toontown.strike import CorporateStrikeGlobals
from toontown.strike.DistributedStrikeEnemyAI import DistributedStrikeEnemyAI
from toontown.suit import SuitTimings

import random
import math
import time


def flip():
    return random.random() > 0.5


def getRandomPoint(pos, radius):
    x = pos[0] + math.ceil(radius*random.random()) * (-1 if flip() else 1)
    y = pos[1] + math.ceil(radius*random.random()) * (-1 if flip() else 1)
    return x, y


class RoundManagerAI:
    SPAWN_RANGES = None
    SPAWN_SPHERES = None
    SPAWN_DELAY = None
    MAX_ENEMIES = None
    TIER_CHART = None

    def __init__(self, strike):
        self.strike = strike
        self.round = 0
        self.intercept = None

        self.spawning = []
        self.enemies = []
        self.destroyed = 0
        self.spawned = 0
        self.roundTarget = 0
        self.roundTransitioning = False
        self.spawnFailures = 0
        self.spawnTaskName = self.uniqueName('cs-spawn-task')
        self.attackTaskName = self.uniqueName('cs-enemy-attack-task')

    def initialize(self):
        self.intercept = random.randint(*self.SPAWN_RANGES[len(self.strike.participants)-1])

    def spawnEnemy(self):
        if self.spawned >= self.roundTarget:
            return False
        livingParticipants = [p for p in self.strike.participants if p.hp > 0]
        if not livingParticipants:
            return False
        self.spawned += 1
        enemy = DistributedStrikeEnemyAI(self.strike.air, self, self.getSuitType())
        self.strike.world.addEnemy(enemy)
        participant = random.choice(livingParticipants)

        spawn = self.SPAWN_SPHERES[random.choice(participant.activeSpheres)]
        x, y = getRandomPoint((spawn[0], spawn[1]), spawn[3])

        navigation = self.strike.world.navigation
        for _ in range(64):
            ground = navigation.floor(x, y)
            if (ground is not None and navigation.standable(ground) and
                    all(math.hypot(px - x, py - y) > 5 for px, py in self.spawning)):
                break
            x, y = getRandomPoint((spawn[0], spawn[1]), spawn[3])
        else:
            self.spawned -= 1
            self.strike.world.removeEnemy(enemy)
            return False

        self.spawning.append((x, y))

        def targetParticipant(task):
            if enemy.dead:
                return task.done
            enemy.targetParticipant(participant)
            enemy.startPosBroadcast()
            return task.done

        def callback(z):
            h = random.randint(0, 359)
            enemy.setInitialPos(x, y, z, h)
            enemy.setNodePosition(x, y, h, z)
            enemy.generateWithRequired(self.strike.zoneId)
            if (x, y) in self.spawning:
                self.spawning.remove((x, y))
            self.enemies.append(enemy)

            taskMgr.doMethodLater(SuitTimings.fromSky + 0.25, targetParticipant,
                                  '%s-target-participant' % id(enemy))

        callback(ground.z)
        return True

    def getSuitType(self):
        unlockedRounds = [round for round in self.TIER_CHART
                          if round <= self.round]
        tier = random.choice(self.TIER_CHART[max(unlockedRounds)])
        return random.choice(CorporateStrikeGlobals.SUIT_TIERS[tier])

    def getEnemyCount(self):
        return int(math.floor(0.2*(self.round**2)+self.intercept) +
                   (math.floor(0.2*((self.round/32)**2)+self.intercept)*(self.round/32)))

    def spawnEnemies(self):
        for _ in range(random.randint(1, 2)):
            self.spawnEnemy()

        taskMgr.add(self.__spawnTask, self.spawnTaskName)
        if not taskMgr.hasTaskNamed(self.attackTaskName):
            taskMgr.add(self.__attackTask, self.attackTaskName)

    def enemyDefeated(self, enemy):
        if enemy not in self.enemies:
            return
        self.enemies.remove(enemy)
        self.destroyed += 1
        self.strike.spawnPowerup(enemy.node.getPos())
        self.strike.world.removeEnemy(enemy)
        taskMgr.doMethodLater(6.5, lambda task: (enemy.requestDelete(), task.done)[1],
                              self.uniqueName('cs-enemy-delete-%s' % enemy.doId))
        self._finishRoundIfReady()

    def _finishRoundIfReady(self):
        if (self.destroyed < self.roundTarget or self.enemies or self.spawning or
                self.roundTransitioning):
            return
        self.roundTransitioning = True
        taskMgr.remove(self.spawnTaskName)
        taskMgr.doMethodLater(4.0, self.__beginNextRound,
                              self.uniqueName('cs-next-round-task'))

    def __beginNextRound(self, task):
        self.roundTransitioning = False
        self.destroyed = 0
        self.nextRound()
        return task.done

    def __attackTask(self, task):
        for enemy in self.enemies[:]:
            if not enemy.canAttack() or enemy.node is None:
                continue
            livingParticipants = [p for p in self.strike.participants
                                  if p.hp > 0 and not p.hasPowerup('disguise')]
            if not livingParticipants:
                continue
            target = min(livingParticipants,
                         key=lambda participant: (participant.node.getPos() - enemy.node.getPos()).length())
            distance = enemy.distanceTo(target)
            goal = self.strike.world.navigation.floor(target.node.getX(), target.node.getY())
            if (distance <= CorporateStrikeGlobals.ENEMY_ATTACK_RANGE and goal is not None and
                    self.strike.world.navigation.segment(enemy.node.getPos(), goal)):
                damage = CorporateStrikeGlobals.getCogAttackDamage(self.round)
                if target.hp > 0:
                    enemy.lastAttack = time.time()
                    target.takeStrikeDamage(damage)
                    enemy.sendUpdate('attack', [target.avId, damage])
        task.setDelay(0.2)
        return task.again

    def __spawnTask(self, task):
        if self.roundTransitioning or self.spawned >= self.roundTarget:
            return task.done
        active = len(self.enemies) + len(self.spawning)
        if active >= self.MAX_ENEMIES:
            task.setDelay(random.randint(*self.SPAWN_DELAY))
            return task.again

        maxAmount = min(self.MAX_ENEMIES - active,
                        self.roundTarget - self.spawned)

        if maxAmount <= 0:
            task.setDelay(random.randint(*self.SPAWN_DELAY))
            return task.again

        amount = random.randint(1, min(maxAmount, 2))

        spawned = False
        for _ in range(amount):
            spawned = self.spawnEnemy() or spawned

        if spawned:
            self.spawnFailures = 0
        else:
            self.spawnFailures += 1
            if self.spawnFailures >= 3:
                self.roundTarget = self.spawned
                self._finishRoundIfReady()
                return task.done

        task.setDelay(random.randint(*self.SPAWN_DELAY))
        return task.again

    def nextRound(self):
        self.round += 1
        self.destroyed = 0
        self.spawned = 0
        self.roundTarget = self.getEnemyCount()
        self.spawnFailures = 0
        self.spawnEnemies()
        self.strike.startRound(self.round)

    def barricadeUnlocked(self):
        for enemy in self.enemies[:]:
            enemy.recoverPath()

    def uniqueName(self, name):
        return '%s-%s' % (name, id(self))
