from .DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
from toontown.strike import CorporateStrikeGlobals


class DistributedCorporateStrikeNPCAI(DistributedNPCToonBaseAI):
    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.strike = None
        self.strikeAmmoVendor = False

    def getStrikeAmmoVendor(self):
        return self.strikeAmmoVendor

    def setStrikeAmmoVendor(self, value):
        self.strikeAmmoVendor = bool(value)

    def d_setStrikeAmmoVendor(self, value):
        self.sendUpdate('setStrikeAmmoVendor', [value])

    def requestEnterStrikeZone(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        if avatar is None or avatar.zoneId != self.zoneId:
            self.notify.warning(
                'Avatar %s tried to use the Corporate Strike dispatch NPC remotely.'
                % avId)
            return

        self.sendUpdateToAvatarId(avId, 'enterStrikeZone', [])

    def requestStrikeAmmoRefill(self):
        if not self.strikeAmmoVendor or self.strike is None:
            return
        avId = self.air.getAvatarIdFromSender()
        participant = next((p for p in self.strike.participants if p.avId == avId), None)
        if participant is None or participant.node is None:
            return
        if (participant.node.getPos() - self.getPos()).length() > \
                CorporateStrikeGlobals.GYRO_AMMO_INTERACT_RANGE:
            return
        hasMissingAmmo = any(
            participant.ammo[gag] < CorporateStrikeGlobals.GAGS[gag]['maxAmmo']
            for gag in CorporateStrikeGlobals.GAGS)
        if not hasMissingAmmo:
            self.sendUpdateToAvatarId(avId, 'strikeAmmoPurchaseResult', [0])
            return
        if not participant.spendPoints(CorporateStrikeGlobals.GYRO_AMMO_REFILL_COST):
            self.sendUpdateToAvatarId(avId, 'strikeAmmoPurchaseResult', [0])
            return
        participant.refillAmmo()
        self.sendUpdateToAvatarId(avId, 'strikeAmmoPurchaseResult', [1])
