from direct.distributed.DistributedObject import DistributedObject
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
import random

from toontown.strike.PointCounter import PointCounter
from toontown.strike.RoundCounter import RoundCounter
from toontown.strike.StrikeGagHud import StrikeGagHud
from toontown.strike.StrikeBarricades import StrikeBarricades
from toontown.toonbase import ToontownGlobals

from pandac.PandaModules import CollisionSphere, CollisionNode


class DistributedCorporateStrike(DistributedObject, FSM):
    ROUND_COUNTER = RoundCounter
    SPAWN_SPHERES = None
    INTRO_MUSIC = 'phase_4/audio/corpstrike/cs_ost_intro.ogg'
    WAVE_MUSIC = (
        'phase_4/audio/corpstrike/cs_ost_bgm_1.ogg',
        'phase_4/audio/corpstrike/cs_ost_bgm_2.ogg',
    )

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, 'DistributedCorporateStrikeFSM')

        self.roundCounter = None
        self.pointCounter = None

        self.geom = None
        self.participants = []
        self.localParticipant = None
        self.gagHud = None
        self.ammoStations = []
        self.barricades = StrikeBarricades(self)
        self.gameOverText = None
        self.gameOverActive = False
        self.strikeMusic = None
        self.musicTaskName = 'strike-music-%s' % id(self)
        self.gameOverTaskName = 'strike-game-over-%s' % id(self)
        self.disguisedAvatars = {}

    def loadEnvironment(self):
        base.transitions.fadeOut(t=0)

        for k in self.SPAWN_SPHERES:
            self.loadSpawnSphere(k, self.SPAWN_SPHERES[k])

        self.barricades.initialize()


    def loadSpawnSphere(self, name, data):
        cs = CollisionSphere(*data)
        cs.setTangible(0)

        name += '-cnode'
        cn = CollisionNode(name)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        cn.addSolid(cs)

        self.accept('enter'+name, self.__enterSpawnSphere)
        self.geom.attachNewNode(cn)

    def __enterSpawnSphere(self, entry):
        name = entry.getIntoNodePath().getName()[:6]
        self.localParticipant.sendUpdate('enterSpawnSphere', [name])

    def setState(self, state):
        self.request(state)

    def setDropPoint(self, x, y, z, h):
        base.localAvatar.setPos(x, y, z)
        base.localAvatar.setH(h)

    def setParticipantIds(self, ids):
        for id in ids:
            p = self.cr.doId2do[id]
            p.setStrike(self)

            if p.avId == base.localAvatar.doId:
                self.localParticipant = p
            else:
                self.participants.append(p)

        self.initializeHud()

    def initializeHud(self):
        self.roundCounter = self.ROUND_COUNTER()
        self.roundCounter.initialize()

        self.pointCounter = PointCounter(self)
        self.pointCounter.initialize()

        self.gagHud = StrikeGagHud(self)
        self.gagHud.initialize()

    def enterLoading(self):
        self.loadEnvironment()
        self.geom.reparentTo(render)

        base.localAvatar.b_setAnimState('TeleportIn', 1)
        self.sendUpdate('barrierDone')

    def exitLoading(self):
        pass

    def enterStrike(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)
        base.localAvatar.b_setAnimState('neutral', 1)
        base.localAvatar.laffMeter.stop()
        self.playIntroMusic()

        base.transitions.fadeOut(t=0)
        fadeTrack = base.transitions.getFadeInIval(t=4)

        Sequence(
            Wait(3),
            Func(fadeTrack.start),
            Wait(2),
            Func(base.cr.playGame.hood.place.fsm.request, 'walk'),
            Func(base.localAvatar.nametag3d.show),
            Func(base.localAvatar.dropShadow.show)
        ).start()

    def exitStrike(self):
        pass

    def disable(self):
        if self.gagHud:
            self.gagHud.destroy()
            self.gagHud = None
        if self.roundCounter:
            self.roundCounter.destroy()
            self.roundCounter = None
        if self.pointCounter:
            self.pointCounter.destroy()
            self.pointCounter = None
        if self.barricades:
            self.barricades.destroy()
            self.barricades = None
        if self.gameOverText:
            self.gameOverText.destroy()
            self.gameOverText = None
        for avId in self.disguisedAvatars:
            toon = self.cr.doId2do.get(avId)
            if toon and toon.isDisguised:
                toon.takeOffSuit()
        self.disguisedAvatars = {}
        taskMgr.remove(self.musicTaskName)
        taskMgr.remove(self.gameOverTaskName)
        if self.strikeMusic:
            self.strikeMusic.stop()
            self.strikeMusic = None
        DistributedObject.disable(self)

    def setRound(self, round):
        self.roundCounter.transitionRound(round)
        if round > 1 and round % 10 == 0:
            base.playSfx(loader.loadSfx('phase_4/audio/corpstrike/cs_alarm.ogg'),
                         volume=0.5)
            base.playSfx(loader.loadSfx('phase_4/audio/corpstrike/cs_ost_boss_wave.ogg'),
                         volume=0.45)

    def playIntroMusic(self):
        self._playMusic(self.INTRO_MUSIC, loop=False)
        taskMgr.doMethodLater(108.1, self._startWaveMusic, self.musicTaskName)

    def _startWaveMusic(self, task):
        self._playMusic(random.choice(self.WAVE_MUSIC), loop=True)
        return task.done

    def _playMusic(self, path, loop):
        if self.strikeMusic:
            self.strikeMusic.stop()
        self.strikeMusic = base.loadMusic(path)
        self.strikeMusic.setLoop(loop)
        self.strikeMusic.play()

    def setBarricadeMask(self, mask):
        if self.barricades:
            self.barricades.setMask(mask)

    def powerupCollected(self, avId, powerupType, duration, suitType):
        if avId == base.localAvatar.doId and self.gagHud:
            self.gagHud.showPowerup(powerupType, duration)
        if powerupType == 'disguise' and suitType:
            toon = self.cr.doId2do.get(avId)
            if toon:
                if toon.isDisguised:
                    toon.takeOffSuit()
                toon.putOnSuit(suitType, setDisplayName=False)
                self.disguisedAvatars[avId] = toon
                taskMgr.doMethodLater(duration, self._removeDisguise,
                                      'strike-disguise-%s-%s' % (id(self), avId),
                                      extraArgs=[avId])

    def _removeDisguise(self, avId, task=None):
        toon = self.disguisedAvatars.pop(avId, None)
        if toon and toon.isDisguised:
            toon.takeOffSuit()
        return task.done if task else None

    def gameOver(self):
        if self.gameOverActive:
            return
        self.gameOverActive = True
        self.gameOverText = OnscreenText(
            text='GAME OVER', pos=(0, 0.05), scale=0.16,
            font=ToontownGlobals.getSuitFont(), fg=(1, 0.25, 0.2, 1),
            shadow=(0, 0, 0, 1), shadowOffset=(0.04, 0.04))
        base.localAvatar.b_setAnimState('Sad', 1)
        status = {
            'loader': 'cogHQLoader', 'where': 'cogHQExterior',
            'how': 'teleportIn', 'hoodId': ToontownGlobals.StrikeZone,
            'zoneId': ToontownGlobals.StrikeZone, 'shardId': None, 'avId': -1,
        }
        taskMgr.doMethodLater(2.5, self._leaveGameOver, self.gameOverTaskName,
                              extraArgs=[status], appendTask=True)

    def _leaveGameOver(self, status, task=None):
        base.cr.playGame.goToStrikeZone(status)
        return task.done if task else None
