from direct.distributed.DistributedObject import DistributedObject
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CollisionNode, CollisionSphere, TextNode

from toontown.strike import StrikePowerupGlobals
from toontown.toonbase import ToontownGlobals


class DistributedStrikePowerup(DistributedObject, DirectObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        DirectObject.__init__(self)
        self.powerupType = None
        self.pos = None
        self.model = None
        self.collider = None
        self.idleSound = None

    def setType(self, powerupType):
        self.powerupType = powerupType

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        if self.powerupType == StrikePowerupGlobals.DOUBLE_POINTS:
            self.model = loader.loadModel('phase_4/models/corpstrike/double_points_powerup')
        elif self.powerupType == StrikePowerupGlobals.EMP:
            self.model = loader.loadModel('phase_4/models/corpstrike/EMP')
            self.model.setScale(0.75)
        else:
            text = TextNode('strike-powerup-label')
            text.setText(StrikePowerupGlobals.LABELS[self.powerupType])
            text.setAlign(TextNode.ACenter)
            text.setFont(ToontownGlobals.getToonFont())
            text.setTextColor(1, 0.9, 0.2, 1)
            self.model = render.attachNewNode(text)
            self.model.setBillboardPointEye()
            self.model.setScale(1.2)
        self.model.reparentTo(render)
        self.model.setPos(*self.pos)
        self.idleSound = loader.loadSfx('phase_4/audio/corpstrike/cs_powerup_idle.ogg')
        self.idleSound.setLoop(False)
        base.playSfx(self.idleSound, node=self.model, volume=0.2)
        self.collider = self.model.attachNewNode(CollisionNode('strike-powerup-%s' % self.doId))
        sphere = CollisionSphere(0, 0, 0.8, 2.0)
        sphere.setTangible(0)
        self.collider.node().addSolid(sphere)
        self.collider.node().setCollideMask(ToontownGlobals.WallBitmask)
        self.acceptOnce('enter' + self.collider.getName(), self._pickup)
        taskMgr.add(self._spin, self.uniqueName('powerup-spin'))

    def _spin(self, task):
        if self.model:
            self.model.setH(self.model.getH() + globalClock.getDt() * 65)
        return task.cont

    def _pickup(self, entry):
        if self.idleSound:
            self.idleSound.stop()
        self.sendUpdate('requestPickup')

    def disable(self):
        taskMgr.remove(self.uniqueName('powerup-spin'))
        self.ignoreAll()
        if self.model:
            self.model.removeNode()
            self.model = None
        if self.idleSound:
            self.idleSound.stop()
            self.idleSound = None
        self.collider = None
        DistributedObject.disable(self)
