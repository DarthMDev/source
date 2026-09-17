from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import DGG, DirectWaitBar
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import (ActorInterval, Func, LerpColorScaleInterval, LerpScaleInterval,
                                            Parallel, ProjectileInterval, Sequence,
                                            Wait)
from panda3d.core import (CollisionHandlerEvent, CollisionHandlerQueue,
                         CollisionNode, CollisionSegment, CollisionSphere,
                         CollisionTraverser,
                         Point3, TextNode)

from toontown.battle import BattleProps
from toontown.toon import LaffMeter
from toontown.strike import CorporateStrikeGlobals
from toontown.strike import StrikePowerupGlobals
from toontown.strike.DistributedStrikeEnemy import DistributedStrikeEnemy
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals


class StrikeGagHud(DirectObject):

    def __init__(self, strike):
        DirectObject.__init__(self)
        self.strike = strike
        self.selectedGag = CorporateStrikeGlobals.GAG_THROW
        self.frame = None
        self.gagText = None
        self.fireButtons = {}
        self.selectButtons = {}
        self.powerMeter = None
        self.healthMeter = None
        self.chargeStart = None
        self.powerTaskName = 'strike-gag-power-%s' % id(self)
        self.powerupIcons = {}
        self.powerupFades = {}
        self.piesAllowed = False

    def initialize(self):
        base.localAvatar.laffMeter.stop()

        self.healthMeter = LaffMeter.LaffMeter(base.localAvatar.style, 100, 100)
        self.healthMeter.reparentTo(base.a2dBottomLeft)
        self.healthMeter.setScale(0.075)
        self.healthMeter.setPos(0.133, 0, 0.13)
        self.healthMeter.start()

        self.frame = DirectFrame(parent=aspect2d, relief=None,
                                 pos=(0, 0, 0.86))
        self.powerMeter = DirectWaitBar(
            parent=self.frame, pos=(0, 0, -0.16), range=100, value=0,
            frameSize=(-0.22, 0.22, -0.025, 0.025), relief=DGG.SUNKEN,
            frameColor=(0.12, 0.12, 0.12, 1), barColor=(0.25, 0.7, 1, 1))
        self.powerMeter.hide()
        base.localAvatar.endAllowPies()
        inventory = base.localAvatar.inventory
        for gagType, track, x in (
            (CorporateStrikeGlobals.GAG_THROW, 4, -0.17),
            (CorporateStrikeGlobals.GAG_SQUIRT, 5, 0.17)):
            gagIcon = (inventory.invModels[track][4],)
            self.fireButtons[gagType] = DirectButton(
                parent=self.frame,
                image=(inventory.upButton, inventory.downButton,
                       inventory.rolloverButton),
                geom=gagIcon, geom_scale=0.85, geom_pos=(-0.01, 0, 0),
                text='', text_scale=0.045, text_align=TextNode.ARight,
                text_fg=(1, 1, 1, 1), text_pos=(0.07, -0.04), relief=None,
                image_color=(0, 0.6, 1, 1), pos=(0, 0, 0))
            self.fireButtons[gagType].bind(DGG.B1PRESS, self.beginFire)
            self.fireButtons[gagType].bind(DGG.B1RELEASE, self.endFire)
            self.selectButtons[gagType] = DirectButton(
                parent=self.frame,
                image=(inventory.upButton, inventory.downButton,
                       inventory.rolloverButton),
                geom=gagIcon, geom_scale=0.48, relief=None,
                pos=(x, 0, -0.09), command=self.selectGag,
                extraArgs=[gagType])

        self.accept(base.INTERACT_KEY, self.beginFire)
        self.accept('%s-up' % base.INTERACT_KEY, self.endFire)
        self.accept('localPieSplat', self.__handlePieSplat)
        self.selectGag(self.selectedGag)
        self.updateHealth(self.strike.localParticipant.hp,
                          self.strike.localParticipant.maxHp)

    def selectGag(self, gagType):
        self._cancelPower()
        self.selectedGag = gagType
        isDisguised = base.localAvatar.doId in self.strike.disguisedAvatars
        if gagType == CorporateStrikeGlobals.GAG_THROW and not isDisguised:
            ammoCount = self.strike.localParticipant.ammo[CorporateStrikeGlobals.GAG_THROW]
            base.localAvatar.setPieType(4)
            base.localAvatar.setNumPies(ammoCount)
            if not self.piesAllowed:
                base.localAvatar.beginAllowPies()
                self.piesAllowed = True
        else:
            if self.piesAllowed:
                base.localAvatar.endAllowPies()
                self.piesAllowed = False
        self.updateAmmo(self.strike.localParticipant.ammo)

    def updateAmmo(self, ammo):
        isDisguised = base.localAvatar.doId in self.strike.disguisedAvatars
        if self.selectedGag == CorporateStrikeGlobals.GAG_THROW and not isDisguised:
            base.localAvatar.setNumPies(ammo[CorporateStrikeGlobals.GAG_THROW])
        for gagType in (CorporateStrikeGlobals.GAG_THROW,
                        CorporateStrikeGlobals.GAG_SQUIRT):
            self.fireButtons[gagType]['text'] = str(ammo[gagType])
            selected = gagType == self.selectedGag
            self.fireButtons[gagType].setBin('fixed', 10 if selected else 9)
            useStockPieButton = (gagType == CorporateStrikeGlobals.GAG_THROW
                                  and not isDisguised)
            if selected and not useStockPieButton:
                self.fireButtons[gagType].show()
            else:
                self.fireButtons[gagType].hide()
            if selected:
                self.selectButtons[gagType]['image_color'] = (1, 0.85, 0.2, 1)
            else:
                self.selectButtons[gagType]['image_color'] = (0.65, 0.65, 0.7, 1)

    def updateHealth(self, hp, maxHp):
        if self.healthMeter and hp is not None and maxHp is not None:
            self.healthMeter.adjustFace(hp, maxHp)

    def beginFire(self, ignored=None):
        if self.strike.barricades and self.strike.barricades.tryPurchase():
            return
        if any(station.tryPurchase() for station in self.strike.ammoStations):
            return
        if self.strike.localParticipant.ammo[self.selectedGag] <= 0:
            base.playSfx(loader.loadSfx('phase_4/audio/sfx/ring_miss.ogg'), volume=0.35)
            return
        isDisguised = base.localAvatar.doId in self.strike.disguisedAvatars
        if self.selectedGag == CorporateStrikeGlobals.GAG_THROW and not isDisguised:
            base.localAvatar._LocalToon__beginTossPieMouse(ignored)
            return
        if self.chargeStart is not None:
            return
        taskMgr.remove(self.powerTaskName)
        self.powerMeter.hide()
        self.chargeStart = globalClock.getFrameTime()
        self.powerMeter['value'] = 0
        self.powerMeter.show()
        taskMgr.add(self.updatePower, self.powerTaskName)

    def endFire(self, ignored=None):
        isDisguised = base.localAvatar.doId in self.strike.disguisedAvatars
        if self.selectedGag == CorporateStrikeGlobals.GAG_THROW and not isDisguised:
            base.localAvatar._LocalToon__endTossPieMouse(ignored)
            return
        if self.chargeStart is None:
            return
        power = self.getPower(globalClock.getFrameTime())
        self._cancelPower()
        self.fireSelected(power)

    def _cancelPower(self):
        self.chargeStart = None
        taskMgr.remove(self.powerTaskName)
        if self.powerMeter:
            self.powerMeter.hide()

    def getPower(self, now):
        rawPower = int((now - self.chargeStart) / 1.25 * 100) % 200
        return 200 - rawPower if rawPower > 100 else rawPower

    def updatePower(self, task):
        self.powerMeter['value'] = self.getPower(globalClock.getFrameTime())
        return task.cont

    def fireSelected(self, power):
        if base.localAvatar.doId in self.strike.disguisedAvatars:
            self.fireDisguised(power)
            return
        self.playGagAnimation(power)

    def fireDisguised(self, power):
        if self.selectedGag == CorporateStrikeGlobals.GAG_SQUIRT:
            self._fireDisguisedHose(power)
            return
        projectile = BattleProps.globalPropPool.getProp('creampie')
        distance = CorporateStrikeGlobals.getGagRange(self.selectedGag, power)
        startPos = base.localAvatar.getPos(render) + base.localAvatar.getQuat(render).getForward()
        startPos.setZ(startPos.getZ() + 2.0)
        targetPos = base.localAvatar.getPos(render) + base.localAvatar.getQuat(render).getForward() * distance
        targetPos.setZ(targetPos.getZ() + 2.0)
        collider = projectile.attachNewNode(CollisionNode('strike-disguise-gag'))
        collider.node().addSolid(CollisionSphere(0, 0, 0, 0.55))
        collider.node().setFromCollideMask(ToontownGlobals.PieBitmask)
        collider.node().setIntoCollideMask(0)
        handler = CollisionHandlerEvent()
        event = 'strike-disguise-hit-%s' % id(collider)
        handler.addInPattern(event)
        self.acceptOnce(event, self.handleProjectileHit,
                        extraArgs=[collider, projectile, power])
        Sequence(Func(projectile.reparentTo, render), Func(projectile.setPos, startPos),
                 Func(base.cTrav.addCollider, collider, handler),
                 ProjectileInterval(projectile, duration=0.38, startPos=startPos,
                                    endPos=targetPos, gravityMult=0.55),
                 Func(base.cTrav.removeCollider, collider),
                 Func(projectile.removeNode)).start()

    def _fireDisguisedHose(self, power):
        toon = base.localAvatar
        distance = CorporateStrikeGlobals.getGagRange(CorporateStrikeGlobals.GAG_SQUIRT, power)
        forward = toon.getQuat(render).getForward()
        startPos = toon.getPos(render) + forward * 1.5
        startPos.setZ(startPos.getZ() + 2.0)
        targetPos = toon.getPos(render) + forward * distance
        targetPos.setZ(toon.getZ(render) + 2.0)
        trav = CollisionTraverser('strike-disguise-hose-trav')
        queue = CollisionHandlerQueue()
        segment = render.attachNewNode(CollisionNode('strike-disguise-hose-segment'))
        segment.node().addSolid(CollisionSegment(startPos[0], startPos[1], startPos[2],
                                                  targetPos[0], targetPos[1], targetPos[2]))
        segment.node().setFromCollideMask(ToontownGlobals.PieBitmask)
        segment.node().setIntoCollideMask(0)
        trav.addCollider(segment, queue)
        trav.traverse(render)
        segment.removeNode()
        hitEnemy = None
        hitPoint = targetPos
        queue.sortEntries()
        for index in range(queue.getNumEntries()):
            entry = queue.getEntry(index)
            intoNp = entry.getIntoNodePath()
            enemy = intoNp.getPythonTag('strikeEnemy')
            if not enemy:
                enemy = intoNp.findNetPythonTag('strikeEnemy')
            if enemy and enemy.hp:
                hitEnemy = enemy
                if entry.hasSurfacePoint():
                    hitPoint = entry.getSurfacePoint(render)
                break
        stream = BattleProps.globalPropPool.getProp('spray')
        stream.reparentTo(render)
        stream.setPos(startPos)
        stream.lookAt(hitPoint)
        stream.setScale(0.28, max(0.5, (hitPoint - startPos).length() / 1.5), 0.28)
        tracks = [Sequence(Func(base.playSfx, loader.loadSfx('phase_5/audio/sfx/firehose_spray.ogg')),
                           Wait(0.65), Func(stream.removeNode))]
        if hitEnemy:
            tracks.append(Sequence(Wait(0.2),
                                   Func(self._showHitEffectAtPoint, hitPoint, hitEnemy),
                                   Func(hitEnemy.sendUpdate, 'requestHit',
                                        [CorporateStrikeGlobals.GAG_SQUIRT, power])))
        Parallel(*tracks).start()

    def playGagAnimation(self, power):
        if self.selectedGag == CorporateStrikeGlobals.GAG_SQUIRT:
            self._playFireHose(power)
        else:
            self._playPieThrow(power)

    def _makeProjectileCollider(self, projectile, eventPrefix, power):
        collider = projectile.attachNewNode(CollisionNode('strike-gag-projectile'))
        collider.node().addSolid(CollisionSphere(0, 0, 0, 0.55))
        collider.node().setFromCollideMask(ToontownGlobals.PieBitmask)
        collider.node().setIntoCollideMask(0)
        handler = CollisionHandlerEvent()
        event = '%s-%s' % (eventPrefix, id(collider))
        handler.addInPattern(event)
        self.acceptOnce(event, self.handleProjectileHit,
                        extraArgs=[collider, projectile, power])
        return collider, handler

    def _playPieThrow(self, power):
        self.fireDisguised(power)

    def _playFireHose(self, power):
        toon = base.localAvatar
        distance = CorporateStrikeGlobals.getGagRange(self.selectedGag, power)
        forward = toon.getQuat(render).getForward()
        startPos = toon.getPos(render) + forward * 1.5
        startPos.setZ(startPos.getZ() + 2.0)
        targetPos = toon.getPos(render) + forward * distance
        targetPos.setZ(toon.getZ(render) + 2.0)

        trav = CollisionTraverser('strike-hose-trav')
        queue = CollisionHandlerQueue()
        segNode = render.attachNewNode(CollisionNode('strike-hose-seg'))
        segNode.node().addSolid(CollisionSegment(startPos[0], startPos[1], startPos[2],
                                                 targetPos[0], targetPos[1], targetPos[2]))
        segNode.node().setFromCollideMask(ToontownGlobals.PieBitmask)
        segNode.node().setIntoCollideMask(0)
        trav.addCollider(segNode, queue)
        trav.traverse(render)
        segNode.removeNode()

        hitEnemy = None
        hitPoint = targetPos
        if queue.getNumEntries() > 0:
            queue.sortEntries()
            for i in range(queue.getNumEntries()):
                entry = queue.getEntry(i)
                intoNp = entry.getIntoNodePath()
                enemy = intoNp.getPythonTag('strikeEnemy')
                if not enemy:
                    enemy = intoNp.findNetPythonTag('strikeEnemy')
                if enemy and enemy.hp:
                    hitEnemy = enemy
                    if entry.hasSurfacePoint():
                        hitPoint = entry.getSurfacePoint(render)
                    break

        hose = BattleProps.globalPropPool.getProp('firehose')
        hydrant = BattleProps.globalPropPool.getProp('hydrant')
        hose.reparentTo(hydrant)
        hose.pose('firehose', 2)
        hydrantNode = toon.attachNewNode('strike-hydrant')
        hydrantNode.clearTransform(toon.getGeomNode().getChild(0))
        hydrantScale = hydrantNode.attachNewNode('strike-hydrant-scale')
        hydrant.reparentTo(hydrantScale)
        toon.pose('firehose', 30)
        toon.update(0)
        torso = toon.getPart('torso', '1000')
        hydrant.setPos(torso, 0, 0, -1.85 if toon.style.torso[0] == 'm' else -1.45)
        hydrant.setPos(0, 0, hydrant.getZ())
        hydrantBase = hydrant.find('**/base')
        if not hydrantBase.isEmpty():
            hydrantBase.setColor(1, 1, 1, 0.5)
            hydrantBase.setPos(toon, 0, 0, 0)
        hydrantNode.detachNode()

        def getStreamOrigin():
            toon.update(0)
            joint = hose.find('**/joint_water_stream')
            if joint.isEmpty():
                return toon.getPos(render) + toon.getQuat(render).getForward()
            point = hidden.attachNewNode('strike-hose-origin')
            point.reparentTo(toon)
            point.setPos(joint.getPos(toon) + Point3(0, -0.55, 0))
            origin = point.getPos(render)
            point.removeNode()
            return origin

        stream = BattleProps.globalPropPool.getProp('spray')

        def showStream():
            orig = getStreamOrigin()
            stream.reparentTo(render)
            stream.setPos(orig)
            stream.lookAt(hitPoint)
            dist = (hitPoint - orig).length()
            stream.setScale(0.28, max(0.5, dist / 1.5), 0.28)

        toonTrack = Sequence(ActorInterval(toon, 'firehose', playRate=1.5),
                             Func(toon.loop, 'neutral'))
        propTrack = Sequence(
            Func(hydrantNode.reparentTo, toon),
            LerpScaleInterval(hydrantScale, 0.2, Point3(1, 1, 1.4),
                              startScale=Point3(1, 1, 0.01)),
            LerpScaleInterval(hydrantScale, 0.1, Point3(1, 1, 1),
                              startScale=Point3(1, 1, 1.4)),
            ActorInterval(hose, 'firehose', playRate=1.5),
            LerpScaleInterval(hydrantScale, 0.15, Point3(1, 1, 0.01),
                              startScale=Point3(1, 1, 1)),
            Func(hydrantNode.removeNode), Func(hose.cleanup), Func(hose.removeNode))

        sprayTrack = Sequence(
            Wait(0.4),
            Func(showStream),
            Func(base.playSfx,
                 loader.loadSfx('phase_5/audio/sfx/firehose_spray.ogg')),
            Wait(0.8),
            Func(stream.removeNode))

        tracks = [toonTrack, propTrack, sprayTrack]

        if hitEnemy:
            def applyHit(enemy=hitEnemy, power=power, point=hitPoint):
                if enemy and enemy.hp:
                    self._showHitEffectAtPoint(point, enemy)
                    enemy.sendUpdate('requestHit', [CorporateStrikeGlobals.GAG_SQUIRT, power])

            hitTrack = Sequence(
                Wait(0.45),
                Func(applyHit))
            tracks.append(hitTrack)

        Parallel(*tracks).start()

    def _startHoseStream(self, stream, collider, handler, startPos, targetPos):
        if callable(startPos):
            startPos = startPos()
        stream.reparentTo(render)
        stream.setPos(startPos)
        stream.lookAt(targetPos)
        distance = (targetPos - startPos).length()
        stream.setScale(0.28, distance / 1.5, 0.28)
        collider.wrtReparentTo(render)
        collider.setPos(targetPos)
        base.cTrav.addCollider(collider, handler)

    def __handlePieSplat(self, pieCode, entry):
        intoNp = entry.getIntoNodePath()
        enemy = intoNp.getPythonTag('strikeEnemy')
        if not enemy:
            enemy = intoNp.findNetPythonTag('strikeEnemy')
        if enemy and enemy.hp:
            enemy.sendUpdate('requestHit', [CorporateStrikeGlobals.GAG_THROW, 100])

    def handleProjectileHit(self, collider, projectile, power, entry):
        base.cTrav.removeCollider(collider)
        enemy = entry.getIntoNodePath().getPythonTag('strikeEnemy')
        if not enemy:
            enemy = entry.getIntoNodePath().findNetPythonTag('strikeEnemy')
        if enemy and enemy.hp:
            self._showHitEffect(entry, enemy)
            enemy.sendUpdate('requestHit', [self.selectedGag, power])

    def _showHitEffect(self, entry, enemy):
        point = (entry.getSurfacePoint(render) if entry.hasSurfacePoint()
                 else enemy.getPos(render) + Point3(0, 0, enemy.getHeight() * 0.65))
        self._showHitEffectAtPoint(point, enemy)

    def _showHitEffectAtPoint(self, point, enemy):
        if self.selectedGag == CorporateStrikeGlobals.GAG_THROW:
            effectName, sound = ('splat-creampie',
                                 'phase_4/audio/sfx/AA_wholepie_only.ogg')
        else:
            effectName, sound = ('splash-from-splat',
                                 'phase_5/audio/sfx/firehose_spray.ogg')
        effect = BattleProps.globalPropPool.getProp(effectName)
        effect.reparentTo(render)
        effect.setPos(point)
        effect.setBillboardPointWorld()
        base.playSfx(loader.loadSfx(sound))
        Sequence(ActorInterval(effect, effectName), Func(effect.cleanup), Func(effect.removeNode)).start()

    def showPowerup(self, powerupType, duration):
        old = self.powerupIcons.pop(powerupType, None)
        if old:
            old[0].destroy()
            old[1].destroy()
        oldFade = self.powerupFades.pop(powerupType, None)
        if oldFade:
            oldFade.finish()
        icon = OnscreenImage(parent=aspect2d, image=StrikePowerupGlobals.ICONS[powerupType],
                             pos=(0.0, 0, -0.72), scale=0.075)
        text = OnscreenText(parent=aspect2d,
                            text=StrikePowerupGlobals.LABELS[powerupType],
                            pos=(0, -0.84), scale=0.035,
                            font=ToontownGlobals.getToonFont(), fg=(1, 0.9, 0.2, 1),
                            shadow=(0, 0, 0, 1))
        self.powerupIcons[powerupType] = (icon, text)
        self._layoutPowerups()
        sound = ('phase_4/audio/corpstrike/cs_powerup_grab_emp.ogg'
                 if powerupType == StrikePowerupGlobals.EMP else
                 'phase_4/audio/corpstrike/cs_powerup_grab_max_ammo.ogg'
                 if powerupType == StrikePowerupGlobals.MAX_AMMO else
                 'phase_4/audio/corpstrike/cs_powerup_grab.ogg')
        base.playSfx(loader.loadSfx(sound), node=base.localAvatar, volume=0.9)
        taskName = 'strike-powerup-%s-%s' % (id(self), powerupType)
        fadeTaskName = '%s-fade' % taskName
        taskMgr.remove(taskName)
        taskMgr.remove(fadeTaskName)
        if powerupType in StrikePowerupGlobals.TIMED_POWERUPS:
            taskMgr.doMethodLater(max(0.0, duration - 5.0), self._fadePowerup,
                                  fadeTaskName, extraArgs=[powerupType])
            taskMgr.doMethodLater(duration, self._hidePowerup,
                                  taskName,
                                  extraArgs=[powerupType])
        else:
            taskMgr.doMethodLater(2.5, self._hidePowerup,
                                  taskName,
                                  extraArgs=[powerupType])

    def _fadePowerup(self, powerupType, task=None):
        widgets = self.powerupIcons.get(powerupType)
        if widgets:
            fade = Parallel(LerpColorScaleInterval(widgets[0], 5.0, (1, 1, 1, 0.2)),
                            LerpColorScaleInterval(widgets[1], 5.0, (1, 1, 1, 0.2)))
            self.powerupFades[powerupType] = fade
            fade.start()
        return task.done if task else None

    def _hidePowerup(self, powerupType, task=None):
        taskMgr.remove('strike-powerup-%s-%s-fade' % (id(self), powerupType))
        fade = self.powerupFades.pop(powerupType, None)
        if fade:
            fade.finish()
        widgets = self.powerupIcons.pop(powerupType, None)
        if widgets:
            widgets[0].destroy()
            widgets[1].destroy()
            if powerupType in StrikePowerupGlobals.TIMED_POWERUPS:
                base.playSfx(loader.loadSfx('phase_4/audio/corpstrike/cs_powerup_expire.ogg'),
                             volume=0.45)
        self._layoutPowerups()
        return task.done if task else None

    def _layoutPowerups(self):
        entries = list(self.powerupIcons.values())
        for index, widgets in enumerate(entries):
            x = (index - (len(entries) - 1) * 0.5) * 0.22
            widgets[0].setPos(x, 0, -0.72)
            widgets[1].setPos(x, -0.84)

    def destroy(self):
        self.ignoreAll()
        self._cancelPower()
        for powerupType in self.powerupIcons:
            taskName = 'strike-powerup-%s-%s' % (id(self), powerupType)
            taskMgr.remove(taskName)
            taskMgr.remove('%s-fade' % taskName)
        if self.frame:
            self.frame.destroy()
            self.frame = None
        if self.healthMeter:
            self.healthMeter.destroy()
            self.healthMeter = None
        self.fireButtons = {}
        self.selectButtons = {}
        for icon, text in self.powerupIcons.values():
            icon.destroy()
            text.destroy()
        self.powerupIcons = {}
        for fade in self.powerupFades.values():
            fade.finish()
        self.powerupFades = {}
        if hasattr(base, 'localAvatar') and base.localAvatar:
            base.localAvatar.endAllowPies()
