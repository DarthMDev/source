from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import Point3

from toontown.strike import CorporateStrikeGlobals


class DistributedStrikeHealthAI(DistributedObjectAI):
    def __init__(self, air, strike, pos):
        DistributedObjectAI.__init__(self, air)
        self.strike = strike
        self.pos = pos
        self.available = True
        self.respawnTask = 'strike-health-respawn-%s' % id(self)

    def getPosition(self):
        return self.pos

    def getAvailable(self):
        return self.available

    def requestPickup(self):
        if not self.available:
            return
        avId = self.air.getAvatarIdFromSender()
        participant = next((p for p in self.strike.participants if p.avId == avId), None)
        if participant is None or participant.node is None:
            return
        if (participant.node.getPos() - Point3(*self.pos)).length() > \
                CorporateStrikeGlobals.HEALTH_TREASURE_PICKUP_RANGE:
            self.sendUpdateToAvatarId(avId, 'setAvailable', [True])
            return
        if not participant.restoreStrikeHp(CorporateStrikeGlobals.HEALTH_TREASURE_HEAL):
            self.sendUpdateToAvatarId(avId, 'setAvailable', [True])
            return
        self.available = False
        self.sendUpdate('setAvailable', [False])
        taskMgr.doMethodLater(CorporateStrikeGlobals.HEALTH_TREASURE_RESPAWN,
                              self._respawn, self.respawnTask)

    def _respawn(self, task):
        self.available = True
        self.sendUpdate('setAvailable', [True])
        return task.done

    def delete(self):
        taskMgr.remove(self.respawnTask)
        DistributedObjectAI.delete(self)
