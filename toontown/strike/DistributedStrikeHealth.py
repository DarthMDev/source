from direct.distributed.DistributedObject import DistributedObject
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import (Func, LerpColorScaleInterval,
                                            LerpPosInterval, Sequence, Wait)
from panda3d.core import CollisionNode, CollisionSphere, Point3, VBase4

from toontown.toonbase import ToontownGlobals


class DistributedStrikeHealth(DistributedObject, DirectObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        DirectObject.__init__(self)
        self.pos = None
        self.available = True
        self.model = None
        self.label = None
        self.collider = None
        self.idleTrack = None
        self.pickupTrack = None
        self.rejectTrack = None
        self.pendingPickup = False
        self.grabSound = None

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def setAvailable(self, available):
        rejected = bool(available) and self.pendingPickup
        self.available = bool(available)
        self._applyAvailability()
        if rejected:
            self._playRejectFeedback()

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.model = loader.loadModel('phase_4/models/props/icecream')
        self.model.reparentTo(render)
        self.model.setPos(*self.pos)
        self.model.setScale(1.15)
        self.model.setBillboardPointEye()
        node = CollisionNode('strike-health-%s' % self.doId)
        sphere = CollisionSphere(0, 0, 0, 1.8)
        sphere.setTangible(0)
        node.addSolid(sphere)
        node.setCollideMask(ToontownGlobals.WallBitmask)
        self.collider = self.model.attachNewNode(node)
        self.accept('enter' + self.collider.getName(), self._pickup)
        self.grabSound = loader.loadSfx('phase_4/audio/sfx/SZ_DD_treasure.ogg')
        self.idleTrack = Sequence(
            LerpPosInterval(self.model, 0.9, self.model.getPos() + Point3(0, 0, 0.25),
                            blendType='easeInOut'),
            LerpPosInterval(self.model, 0.9, self.model.getPos(), blendType='easeInOut'))
        self.idleTrack.loop()
        self._applyAvailability()

    def _pickup(self, entry):
        if self.available and not self.pendingPickup:
            self.pendingPickup = True
            self.sendUpdate('requestPickup')

    def _applyAvailability(self):
        if not self.model or not self.collider:
            return
        if self.available:
            if self.pickupTrack:
                self.pickupTrack.finish()
                self.pickupTrack = None
            self.pendingPickup = False
            self.model.wrtReparentTo(render)
            self.model.setPos(*self.pos)
            self.model.show()
            self.collider.unstash()
        else:
            self.collider.stash()
            if self.pendingPickup:
                self._playPickupFeedback()
            else:
                self.model.hide()

    def _playPickupFeedback(self):
        self.pendingPickup = False
        if self.grabSound:
            base.playSfx(self.grabSound, node=self.model)
        self.model.wrtReparentTo(base.localAvatar)
        if self.idleTrack:
            self.idleTrack.pause()
        self.pickupTrack = Sequence(
            LerpPosInterval(self.model, 0.55, Point3(0, 0, 3),
                            startPos=self.model.getPos(), blendType='easeInOut'),
            Func(self.model.hide),
            Func(self._finishPickupFeedback))
        self.pickupTrack.start()

    def _playRejectFeedback(self):
        self.pendingPickup = False
        if self.rejectTrack:
            self.rejectTrack.finish()
        if self.grabSound:
            base.playSfx(loader.loadSfx('phase_4/audio/sfx/ring_miss.ogg'),
                         node=self.model)
        self.collider.stash()
        self.rejectTrack = Sequence(
            LerpColorScaleInterval(self.model, 0.25, VBase4(0, 0, 0, 0),
                                   startColorScale=VBase4(1, 1, 1, 1)),
            Wait(0.3),
            LerpColorScaleInterval(self.model, 0.25, VBase4(1, 1, 1, 1),
                                   startColorScale=VBase4(0, 0, 0, 0)),
            Func(self.collider.unstash),
            Func(self._finishRejectFeedback))
        self.rejectTrack.start()

    def _finishRejectFeedback(self):
        self.rejectTrack = None

    def _finishPickupFeedback(self):
        self.pickupTrack = None
        if self.model:
            self.model.wrtReparentTo(render)
            self.model.setPos(*self.pos)

    def disable(self):
        self.ignoreAll()
        if self.idleTrack:
            self.idleTrack.finish()
            self.idleTrack = None
        if self.pickupTrack:
            self.pickupTrack.finish()
            self.pickupTrack = None
        if self.rejectTrack:
            self.rejectTrack.finish()
            self.rejectTrack = None
        if self.model:
            self.model.removeNode()
            self.model = None
        self.collider = None
        self.label = None
        DistributedObject.disable(self)
