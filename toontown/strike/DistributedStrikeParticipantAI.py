from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.strike import CorporateStrikeGlobals
from toontown.strike import StrikePowerupGlobals
from toontown.toonbase import ToontownGlobals
from otp.otpbase import OTPGlobals

import time
import math

from pandac.PandaModules import CollisionSphere, CollisionNode, NodePath


class DistributedStrikeParticipantAI(DistributedObjectAI):
    MAX_MOVE_SPEED = (OTPGlobals.ToonForwardSpeed *
                      ToontownGlobals.BMovementSpeedMultiplier)
    MOVE_TOLERANCE = 0.5

    def __init__(self, air, strike, avId):
        DistributedObjectAI.__init__(self, air)

        self.strike = strike
        self.node = None
        self.flock = None
        self.activeSpheres = ['spawn1', 'spawn2']

        self.avId = avId
        self.points = 500
        self.hp = 100
        self.maxHp = 100
        self.ammo = [CorporateStrikeGlobals.GAGS[gag]['maxAmmo']
                     for gag in (CorporateStrikeGlobals.GAG_THROW,
                                 CorporateStrikeGlobals.GAG_SQUIRT)]
        self.powerups = {}
        self.lastPositionTime = None

    def registerFlock(self, node, flock):
        self.node = node
        self.flock = flock

        cs = CollisionSphere(0, 0, 0, 2)
        cnp = self.node.attachNewNode(CollisionNode('cnode'))
        cnp.node().addSolid(cs)

    def setPosition(self, x, y, h):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId or self.node is None:
            return
        now = time.time()
        if self.lastPositionTime is not None:
            distance = math.hypot(x - self.node.getX(), y - self.node.getY())
            maximum = self.MAX_MOVE_SPEED * (now - self.lastPositionTime) + self.MOVE_TOLERANCE
            if distance > maximum:
                return
        self.node.setX(x)
        self.node.setY(y)
        self.node.setH(h)
        self.lastPositionTime = now

    def enterSpawnSphere(self, name):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            return

        if name in self.activeSpheres:
            self.activeSpheres.remove(name)
            self.activeSpheres.insert(0, name)
            return

        self.activeSpheres.insert(0, name)
        if len(self.activeSpheres) == 3:
            self.activeSpheres.pop()

    def unlockSpawnSphere(self, name):
        if name not in self.activeSpheres:
            self.activeSpheres.append(name)

    def getAvId(self):
        return self.avId

    def getPoints(self):
        return self.points

    def getHp(self):
        return self.hp

    def getMaxHp(self):
        return self.maxHp

    def getAmmo(self):
        return tuple(self.ammo)

    def d_setAmmo(self):
        self.sendUpdate('setAmmo', self.getAmmo())

    def addPoints(self, points):
        if self.hasPowerup(StrikePowerupGlobals.DOUBLE_POINTS):
            points *= 2
        self.points += points
        self.sendUpdate('setPoints', [self.points])

    def spendPoints(self, points):
        if self.points < points:
            return False
        self.points -= points
        self.sendUpdate('setPoints', [self.points])
        return True

    def consumeAmmo(self, gagType):
        if self.ammo[gagType] <= 0:
            return False
        self.ammo[gagType] -= 1
        self.d_setAmmo()
        return True

    def takeStrikeDamage(self, damage):
        self.hp = max(0, self.hp - damage)
        self.sendUpdate('setHp', [self.hp])
        if self.hp == 0:
            self.strike.checkGameOver()

    def restoreStrikeHp(self, amount):
        if self.hp <= 0 or self.hp >= self.maxHp:
            return False
        self.hp = min(self.maxHp, self.hp + amount)
        self.sendUpdate('setHp', [self.hp])
        return True

    def activatePowerup(self, powerupType):
        self.powerups[powerupType] = time.time() + StrikePowerupGlobals.DURATION

    def hasPowerup(self, powerupType):
        return self.powerups.get(powerupType, 0) > time.time()

    def refillAmmo(self):
        self.ammo = [CorporateStrikeGlobals.GAGS[gag]['maxAmmo']
                     for gag in (CorporateStrikeGlobals.GAG_THROW,
                                 CorporateStrikeGlobals.GAG_SQUIRT)]
        self.d_setAmmo()

    def refillGag(self, gagType):
        if gagType not in CorporateStrikeGlobals.GAGS:
            return
        self.ammo[gagType] = CorporateStrikeGlobals.GAGS[gagType]['maxAmmo']
        self.d_setAmmo()
