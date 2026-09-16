from direct.directnotify import DirectNotifyGlobal
from . import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.classicchars import DistributedMickeyAI
from toontown.toon import NPCToons


class TTHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("TTHoodDataAI")

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.ToontownCentral
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)

        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        trolley.start()
        self.addDistObj(trolley)
        self.trolley = trolley

        self.classicChar = DistributedMickeyAI.DistributedMickeyAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()
        self.addDistObj(self.classicChar)

        resistanceScout = NPCToons.createNPC(
            self.air,
            91921,
            (self.zoneId, 'Resistance Scout',
             ('dls', 'ms', 'm', 'm', 6, 0, 6, 6, 0, 10, 0, 10, 2, 9),
             'm', 1, NPCToons.NPC_CORPORATE_STRIKE),
            self.zoneId)
        resistanceScout.d_setPos(15.5, 21.0, 4.0)
        resistanceScout.d_setH(90.0)
        self.addDistObj(resistanceScout)
        self.resistanceScout = resistanceScout

        messenger.send("TTHoodSpawned", [self])

    def shutdown(self):
        """Do base class shutdown then tell costume manager."""
        HoodDataAI.HoodDataAI.shutdown(self)
        messenger.send("TTHoodDestroyed", [self])
