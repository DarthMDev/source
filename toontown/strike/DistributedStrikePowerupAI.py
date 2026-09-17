from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import Point3

from toontown.strike import StrikePowerupGlobals


class DistributedStrikePowerupAI(DistributedObjectAI):
    PICKUP_RANGE = 7.0

    def __init__(self, air, strike, powerupType, pos):
        DistributedObjectAI.__init__(self, air)
        self.strike = strike
        self.powerupType = powerupType
        self.pos = pos
        self.collected = False

    def getType(self):
        return self.powerupType

    def getPosition(self):
        return self.pos

    def requestPickup(self):
        if self.collected:
            return
        avId = self.air.getAvatarIdFromSender()
        participant = next((p for p in self.strike.participants if p.avId == avId), None)
        if participant is None or participant.node is None:
            return
        if (participant.node.getPos() - Point3(*self.pos)).length() > self.PICKUP_RANGE:
            return
        self.collected = True
        self.strike.applyPowerup(participant, self.powerupType)
        self.requestDelete()
