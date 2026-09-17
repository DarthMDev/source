from direct.distributed import DistributedSmoothNode
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import *

from toontown.battle import BattleProps
from toontown.battle import SuitBattleGlobals
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout
from toontown.strike import CorporateStrikeGlobals
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitTimings
from toontown.suit.SuitDNA import SuitDNA
from toontown.suit.Suit import Suit

from pandac.PandaModules import CollisionNode, CollisionSphere, SmoothMover, Point3, VBase4, Vec3


class DistributedStrikeEnemy(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

        self.type = None
        self.avatar = None
        self.initialPos = None
        self.initialH = None
        self.hp = None
        self.maxHp = None
        self.level = None

        self.prop = None
        self.suitName = None
        self.hitCollider = None
        self.landing = True
        self.flying = False
        self.pendingPosition = None
        self.flightTrack = None
        self.postFlightTaskName = None
        self.attackTrack = None
        self.dead = False
        self.walkUntil = 0.0

        self.smoother = SmoothMover()
        self.smoother.setSmoothMode(SmoothMover.SMOn)
        self.smoother.setPredictionMode(SmoothMover.PMOff)
        self.smoother.setDelay(DistributedSmoothNode.PredictionLag)

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.postFlightTaskName = self.uniqueName('post-flight')

        dna = SuitDNA()
        dna.newSuit(name=self.type)

        self.avatar = Suit()
        self.avatar.setDNA(dna)
        self.avatar.loop('walk')
        self.avatar.setH(self.initialH)
        self.avatar.reparentTo(render)
        self.suitName = self.avatar.getName()
        self.hitCollider = self.avatar.attachNewNode(CollisionNode('strike-cog-hit'))
        self.hitCollider.node().addSolid(CollisionSphere(0, 0,
                                                         self.avatar.getHeight() * 0.5,
                                                         CorporateStrikeGlobals.SUIT_RADII[self.type]))
        self.hitCollider.node().setIntoCollideMask(ToontownGlobals.PieBitmask)
        self.hitCollider.setPythonTag('strikeEnemy', self)
        self.updateHealthLabel()

        self.spawn()

        taskMgr.add(self.__smoothPosition, self.uniqueName('smooth-position'))

    def spawn(self):
        skyPos = Point3(self.initialPos)
        skyPos.setZ(self.initialPos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)

        groundF = 28
        dur = self.avatar.getDuration('landing')
        fr = self.avatar.getFrameRate('landing')
        animTimeInAir = groundF / fr
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir

        self.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8

        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame+1) / fr

        lerpPosTrack = Sequence(Func(self.avatar.setH, self.initialH),
                                self.avatar.posInterval(timeTillLanding, self.initialPos, startPos=skyPos),
                                Wait(impactLength))
        fadeInTrack = Sequence(Func(self.avatar.setTransparency, 1),
                               self.avatar.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1),
                                                              startColorScale=VBase4(1, 1, 1, 0)),
                               Func(self.avatar.clearColorScale), Func(self.avatar.clearTransparency))
        animTrack = Sequence(Func(self.avatar.pose, 'landing', 0), Wait(waitTime),
                             ActorInterval(self.avatar, 'landing', duration=dur),
                             Func(self.avatar.loop, 'walk'))

        self.attachPropeller()

        propInSound = base.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        propTrack = Parallel(SoundInterval(propInSound, duration=waitTime+dur, node=self.avatar),
                             Sequence(
                                 ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=waitTime+spinTime,
                                               startTime=0.0, endTime=spinTime),
                                 ActorInterval(self.prop, 'propeller', duration=propDur-openTime, startTime=openTime),
                                 Func(self.detachPropeller)))

        Sequence(
            Parallel(lerpPosTrack, fadeInTrack, animTrack, propTrack, name=self.uniqueName('trackName')),
            Func(self.setToInitialPos)
        ).start()

    def attachPropeller(self):
        if self.prop is None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')

        head = self.avatar.find('**/joint_head')
        self.prop.reparentTo(head)

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None

    def setToInitialPos(self):
        self.smoother.clearPositions(0)
        self.smoother.setPos(self.initialPos)
        self.smoother.setH(self.initialH)
        self.smoother.setPhonyTimestamp()
        self.smoother.markPosition()
        self.smoother.applySmoothPosHpr(self.avatar, self.avatar)
        self.smoother.clearPositions(1)
        self.landing = False
        if self.pendingPosition:
            position = self.pendingPosition
            self.pendingPosition = None
            self.setPosition(*position)

    def __smoothPosition(self, task):
        if self.dead or self.landing or self.flying:
            return task.cont
        previous = self.avatar.getPos()
        self.smoother.computeAndApplySmoothPosHpr(self.avatar, self.avatar)
        if (self.avatar.getPos() - previous).lengthSquared() > 0.00001:
            self.walkUntil = globalClock.getFrameTime() + 0.2
        if not self.attackTrack and not taskMgr.hasTaskNamed(self.postFlightTaskName):
            animation = 'walk' if globalClock.getFrameTime() < self.walkUntil else 'neutral'
            if self.avatar.getCurrentAnim() != animation:
                self.avatar.loop(animation)
        return task.cont

    def setType(self, type):
        self.type = type

    def setInitialPos(self, x, y, z, h):
        self.initialPos = Point3(x, y, z)
        self.initialH = h

    def setPosition(self, x, y, z, h, timestamp):
        if self.landing or self.flying:
            self.pendingPosition = (x, y, z, h, timestamp)
            return
        self.smoother.setPos(x, y, z)
        self.smoother.setH(h)

        now = globalClock.getFrameTime()
        local = globalClockDelta.networkToLocalTime(timestamp, now)

        self.smoother.setTimestamp(local)
        self.smoother.markPosition()

    def flyTo(self, x, y, z, h):
        if not self.avatar or self.landing or self.dead:
            return
        self._stopAttack()
        if self.postFlightTaskName:
            taskMgr.remove(self.postFlightTaskName)
        if self.flightTrack:
            self.flightTrack.pause()
            self.flightTrack = None
        target = Point3(x, y, z)
        start = self.avatar.getPos(render)
        startAir = Point3(start)
        targetAir = Point3(target)
        startAir.setZ(startAir.getZ() + 8.0)
        targetAir.setZ(targetAir.getZ() + 8.0)
        self.smoother.clearPositions(1)
        self.attachPropeller()
        prop = self.prop
        duration = 1.4
        self.flying = True
        flight = Parallel(
            Sequence(self.avatar.posInterval(0.25, startAir, startPos=start),
                     self.avatar.posInterval(0.9, targetAir, startPos=startAir),
                     self.avatar.posInterval(0.25, target, startPos=targetAir)),
            ActorInterval(prop, 'propeller', constrainedLoop=1, duration=duration),
            SoundInterval(loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg'),
                          duration=duration, node=self.avatar))
        self.flightTrack = Sequence(Func(self.avatar.setH, h), Func(self.avatar.loop, 'neutral'),
                                    flight, Func(self._finishFlight, target, h))
        self.flightTrack.start()

    def _finishFlight(self, target, h):
        self.avatar.setPos(target)
        self.avatar.setH(h)
        self.detachPropeller()
        self.avatar.loop('neutral')
        self.smoother.clearPositions(0)
        self.smoother.setPos(target)
        self.smoother.setH(h)
        self.smoother.setPhonyTimestamp()
        self.smoother.markPosition()
        self.smoother.applySmoothPosHpr(self.avatar, self.avatar)
        self.smoother.clearPositions(1)
        self.flying = False
        self.flightTrack = None
        self.pendingPosition = None
        taskMgr.doMethodLater(0.35, self._resumeWalk, self.postFlightTaskName)

    def _resumeWalk(self, task):
        return task.done

    def _stopAttack(self):
        if self.attackTrack:
            self.attackTrack.pause()
            self.attackTrack = None
        if self.avatar:
            self.avatar.clearChat()

    def _finishAttack(self):
        self.attackTrack = None
        if self.avatar:
            self.avatar.clearChat()
            self.avatar.loop('neutral')

    def setMaxHp(self, maxHp):
        self.maxHp = maxHp
        self.updateHealthLabel()

    def setLevel(self, level):
        self.level = level
        self.updateHealthLabel()

    def setHp(self, hp):
        self.hp = hp
        self.updateHealthLabel()

    def updateHealthLabel(self):
        if not self.avatar or self.hp is None or self.maxHp is None:
            return
        levelText = 'Lv. %d' % self.level if self.level is not None else 'Lv. ?'
        self.avatar.setName('%s\n%s\n%d/%d' % (self.suitName, levelText,
                                                 self.hp, self.maxHp))

    def hit(self, avId, gagType, damage):
        if not self.avatar:
            return
        impactName = ('splat-creampie' if gagType == 0 else
                      'splash-from-splat')
        impactSound = ('phase_4/audio/sfx/AA_wholepie_only.ogg' if gagType == 0 else
                       'phase_4/audio/sfx/firehose_spray.ogg')
        impact = BattleProps.globalPropPool.getProp(impactName)
        impact.setBillboardPointWorld()
        Sequence(
            Func(impact.reparentTo, render),
            Func(impact.setPos, self.avatar, 0, 0,
                 self.avatar.getHeight() * 0.6),
            SoundInterval(loader.loadSfx(impactSound), node=self.avatar,
                          volume=0.8),
            ActorInterval(impact, impactName),
            Func(impact.cleanup),
            Func(impact.removeNode)).start()
        self.avatar.colorScaleInterval(0.15, VBase4(1, 0.3, 0.3, 1),
                                       startColorScale=VBase4(1, 1, 1, 1)).start()
        if self.hp is not None and damage >= self.hp:
            taskMgr.doMethodLater(0.4, self.beginDeath,
                                  self.uniqueName('strike-death'))

    def beginDeath(self, task):
        if not self.avatar:
            return task.done
        self.dead = True
        self._stopAttack()
        if self.flightTrack:
            self.flightTrack.pause()
            self.flightTrack = None
        self.detachPropeller()
        deathSuit = self.avatar.getLoseActor()
        self.avatar.hide()
        deathSuit.reparentTo(render)
        deathSuit.setPosHpr(self.avatar.getPos(render), self.avatar.getHpr(render))
        deathSuit.setScale(self.avatar.getScale())
        spinSound = loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
        fallSound = loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        Sequence(
            Parallel(
                ActorInterval(deathSuit, 'lose', duration=6.0),
                Sequence(SoundInterval(spinSound, duration=3.0,
                                       startTime=0.6, volume=0.8),
                         Wait(2.2),
                         SoundInterval(fallSound, volume=0.32))),
            Func(deathSuit.detachNode),
            Func(self.avatar.cleanupLoseActor)).start()
        return task.done

    def attack(self, avId, damage):
        if self.avatar and not self.dead and not self.landing and not self.flying:
            baseLevel = SuitBattleGlobals.SuitAttributes[self.type]['level']
            relativeLevel = max(0, min(4, (self.level or 1) - baseLevel))
            attack = SuitBattleGlobals.getSuitAttack(self.type, relativeLevel)
            if attack:
                self._stopAttack()
                target = self.cr.doId2do.get(avId)
                if target:
                    self.avatar.headsUp(target)
                taunt = SuitBattleGlobals.getAttackTaunt(attack['name'])
                self.attackTrack = Sequence(Func(self.avatar.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(self.avatar, attack['animName']),
                         Func(self._finishAttack))
                self.attackTrack.start()
        if avId == base.localAvatar.doId:
            base.playSfx(loader.loadSfx('phase_3.5/audio/sfx/tt_s_ara_mat_slip.ogg'),
                         volume=0.35)

    def disable(self):
        self._stopAttack()
        taskMgr.remove(self.uniqueName('smooth-position'))
        if self.hitCollider:
            self.hitCollider.removeNode()
            self.hitCollider = None
        if self.prop:
            self.detachPropeller()
        if self.flightTrack:
            self.flightTrack.pause()
            self.flightTrack = None
        if self.postFlightTaskName:
            taskMgr.remove(self.postFlightTaskName)
        if self.avatar:
            self.avatar.cleanup()
            self.avatar.removeNode()
            self.avatar = None
        DistributedObject.disable(self)
