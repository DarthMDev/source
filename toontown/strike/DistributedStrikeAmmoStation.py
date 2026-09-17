from direct.distributed.DistributedObject import DistributedObject
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionNode, CollisionSphere, TextNode

from toontown.strike import CorporateStrikeGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals


class DistributedStrikeAmmoStation(DistributedObject, DirectObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        DirectObject.__init__(self)
        self.strikeId = None
        self.strike = None
        self.pos = None
        self.heading = 0
        self.gagType = None
        self.cost = CorporateStrikeGlobals.WALL_AMMO_REFILL_COST
        self.model = None
        self.gagIcon = None
        self.collider = None
        self.prompt = None
        self.nearby = False

    def setStrikeId(self, strikeId):
        self.strikeId = strikeId
        self.strike = self.cr.doId2do.get(strikeId)
        if self.strike and self not in self.strike.ammoStations:
            self.strike.ammoStations.append(self)

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def setHeading(self, heading):
        self.heading = heading

    def setGagType(self, gagType):
        self.gagType = gagType

    def setCost(self, cost):
        self.cost = cost

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.setStrikeId(self.strikeId)
        self.model = loader.loadModel('phase_4/models/cogHQ/gagTank')
        self.model.reparentTo(render)
        self.model.setH(self.heading)
        self.model.setScale(0.5)
        self.model.find('**/gagLabelDCS').hide()
        bounds = self.model.getTightBounds()
        groundZ = self.pos[2]
        if bounds:
            groundZ -= bounds[0].getZ()
        self.model.setPos(self.pos[0], self.pos[1], groundZ)
        gagNode = self.model.attachNewNode('strike-ammo-gag-icon')
        gagNode.setPosHpr(0.0, -2.62, 4.0, 0, 0, 0)
        gagNode.setColorScale(0.7, 0.7, 0.6, 1)
        track = (ToontownBattleGlobals.THROW_TRACK
                 if self.gagType == CorporateStrikeGlobals.GAG_THROW
                 else ToontownBattleGlobals.SQUIRT_TRACK)
        icons = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        iconName = ToontownBattleGlobals.AvPropsNew[track][4]
        self.gagIcon = icons.find('**/' + iconName).copyTo(gagNode)
        self.gagIcon.setScale(13.0)
        self.gagIcon.setPos(0, -0.1, 0)
        icons.removeNode()
        node = CollisionNode('strike-ammo-station-%s' % self.doId)
        sphere = CollisionSphere(0, 0, 1.4, 3.0)
        sphere.setTangible(0)
        node.addSolid(sphere)
        node.setCollideMask(ToontownGlobals.WallBitmask)
        self.collider = self.model.attachNewNode(node)
        self.accept('enter' + self.collider.getName(), self._enter)
        self.accept('exit' + self.collider.getName(), self._exit)
        self.prompt = OnscreenText(parent=aspect2d, text='', pos=(0, -0.72),
                                   scale=0.042, align=TextNode.ACenter,
                                   font=ToontownGlobals.getToonFont(),
                                   fg=(1, 0.9, 0.25, 1), shadow=(0, 0, 0, 1))
        self.prompt.hide()
        taskMgr.add(self._checkProximity, 'strike-ammo-proximity-%s' % self.doId)

    def _enter(self, entry):
        self._setNearby(True)

    def _exit(self, entry):
        self._setNearby(False)

    def _setNearby(self, nearby):
        if self.nearby == nearby:
            return
        self.nearby = nearby
        if nearby:
            self.prompt.setText('REFILL %s  -  %s POINTS\n[ %s ]' %
                                (CorporateStrikeGlobals.GAGS[self.gagType]['name'].upper(), self.cost,
                                 base.INTERACT_KEY.upper()))
            self.prompt.show()
        elif self.prompt:
            self.prompt.hide()

    def _checkProximity(self, task):
        if not self.model or not hasattr(base, 'localAvatar') or not base.localAvatar:
            return task.cont
        nearby = ((base.localAvatar.getPos(render) - self.model.getPos(render)).length()
                  <= CorporateStrikeGlobals.WALL_AMMO_INTERACT_RANGE)
        self._setNearby(nearby)
        task.setDelay(0.15)
        return task.again

    def tryPurchase(self):
        if not self.nearby:
            return False
        self.sendUpdate('requestRefill')
        return True

    def refillResult(self, success):
        if success:
            base.playSfx(loader.loadSfx('phase_4/audio/corpstrike/cs_purchase.ogg'), volume=0.6)
        else:
            base.playSfx(loader.loadSfx('phase_4/audio/sfx/ring_miss.ogg'), volume=0.5)

    def disable(self):
        self.ignoreAll()
        taskMgr.remove('strike-ammo-proximity-%s' % self.doId)
        if self.strike and self in self.strike.ammoStations:
            self.strike.ammoStations.remove(self)
        if self.prompt:
            self.prompt.destroy()
            self.prompt = None
        if self.gagIcon:
            self.gagIcon.removeNode()
            self.gagIcon = None
        if self.model:
            self.model.removeNode()
            self.model = None
        self.collider = None
        DistributedObject.disable(self)
