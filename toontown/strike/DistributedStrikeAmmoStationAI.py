from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import Point3

from toontown.strike import CorporateStrikeGlobals


class DistributedStrikeAmmoStationAI(DistributedObjectAI):
    def __init__(self, air, strike, posHpr, gagType):
        DistributedObjectAI.__init__(self, air)
        self.strike = strike
        self.posHpr = posHpr
        self.gagType = gagType

    def getStrikeId(self):
        return self.strike.doId

    def getPosition(self):
        return self.posHpr[:3]

    def getHeading(self):
        return self.posHpr[3]

    def getGagType(self):
        return self.gagType

    def getCost(self):
        return CorporateStrikeGlobals.WALL_AMMO_REFILL_COST

    def requestRefill(self):
        avId = self.air.getAvatarIdFromSender()
        participant = next((p for p in self.strike.participants if p.avId == avId), None)
        if participant is None or participant.node is None:
            return
        if (participant.node.getPos() - Point3(*self.posHpr[:3])).length() > \
                CorporateStrikeGlobals.WALL_AMMO_INTERACT_RANGE:
            return
        if participant.ammo[self.gagType] >= CorporateStrikeGlobals.GAGS[self.gagType]['maxAmmo']:
            self.sendUpdateToAvatarId(avId, 'refillResult', [0])
            return
        if not participant.spendPoints(CorporateStrikeGlobals.WALL_AMMO_REFILL_COST):
            self.sendUpdateToAvatarId(avId, 'refillResult', [0])
            return
        participant.refillGag(self.gagType)
        self.sendUpdateToAvatarId(avId, 'refillResult', [1])
