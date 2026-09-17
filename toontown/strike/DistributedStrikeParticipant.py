from direct.distributed.DistributedObject import DistributedObject


class DistributedStrikeParticipant(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

        self.strike = None
        self.avId = None
        self.points = None

        self.hp = None
        self.maxHp = None
        self.ammo = (0, 0)

    def setStrike(self, strike):
        self.strike = strike

    def setAvId(self, avId):
        self.avId = avId

    def setPoints(self, points):
        self.points = points
        if self.strike and getattr(self.strike, 'pointCounter', None):
            label = self.strike.pointCounter.pointLabels.get(self.avId)
            if label:
                label.updatePoints(points)

    def setHp(self, hp):
        oldHp = self.hp
        self.hp = hp
        if self.isOurs() and oldHp is not None and hp != oldHp:
            base.localAvatar.showHpText(hp - oldHp)
        if self.isOurs() and self.strike and getattr(self.strike, 'gagHud', None):
            self.strike.gagHud.updateHealth(self.hp, self.maxHp)

    def setMaxHp(self, maxHp):
        self.maxHp = maxHp
        if self.isOurs() and self.strike and getattr(self.strike, 'gagHud', None):
            self.strike.gagHud.updateHealth(self.hp, self.maxHp)

    def setAmmo(self, throwAmmo, squirtAmmo):
        self.ammo = (throwAmmo, squirtAmmo)
        if self.isOurs() and self.strike and getattr(self.strike, 'gagHud', None):
            self.strike.gagHud.updateAmmo(self.ammo)

    def isOurs(self):
        return self.avId == base.localAvatar.doId

    def announceGenerate(self):
        if self.isOurs():
            taskMgr.add(self.__broadcastPosition, 'broadcast-position-%s' % id(self))

    def __broadcastPosition(self, task):
        pos = base.localAvatar.getPos()
        self.sendUpdate('setPosition', [pos[0], pos[1]])
        return task.cont

    def disable(self):
        taskMgr.remove('broadcast-position-%s' % id(self))
        self.strike = None
        DistributedObject.disable(self)
