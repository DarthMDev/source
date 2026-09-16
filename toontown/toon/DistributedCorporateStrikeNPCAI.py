from .DistributedNPCToonBaseAI import DistributedNPCToonBaseAI


class DistributedCorporateStrikeNPCAI(DistributedNPCToonBaseAI):
    def requestEnterStrikeZone(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        if avatar is None or avatar.zoneId != self.zoneId:
            self.notify.warning(
                'Avatar %s tried to use the Corporate Strike dispatch NPC remotely.'
                % avId)
            return

        self.sendUpdateToAvatarId(avId, 'enterStrikeZone', [])
