# Boot up just a portion of Toontown

import gc
import random

gc.disable()

from pandac.PandaModules import *
import os

loadPrcFile('config/general.prc')
loadPrcFile('config/distribution/dev.prc')

import __builtin__

__builtin__.settings = {}
__builtin__.process = 'client'

from toontown.launcher.TTILauncher import TTILauncher
launcher = TTILauncher()
__builtin__.launcher = launcher


from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
from toontown.toonbase import ToonBase
ToonBase.ToonBase()
base.graphicsEngine.renderFrame()
DirectGuiGlobals.setDefaultRolloverSound(base.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(base.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
base.initNametagGlobals()
__builtin__.loader = base.loader

from toontown.toon import Toon
from toontown.suit import Suit

gc.enable()
gc.collect()

class ClientRepository:
    def __getattr__(self, item):
        return None

__builtin__.cr = ClientRepository()
base.cr = cr

# ----- Movie Code starts here ----- #

from toontown.toon import ToonDNA
from toontown.suit import SuitDNA
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import CompassEffect, NodePath
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.filter.CommonFilters import CommonFilters
from toontown.util.PlacerTool3D import PlacerTool3D

base.camLens.setNearFar(1, 10000)

# Scene 1
toontownCentral = loader.loadModel('phase_4/models/neighborhoods/toontown_central_sz')
toontownCentral.reparentTo(render)

blimp = Actor("phase_4/models/corpstrike/blimp_mod.bam", {"flying": "phase_4/models/corpstrike/blimp_chan_flying.bam"})
blimp.reparentTo(render)
blimp.setPosHpr(-2, -304, 81, 145, 0, 0)
blimp.loop('flying')
blimpTV = loader.loadModel('phase_4/models/corpstrike/blimp_tv.bam')
blimpTV.reparentTo(blimp)

# Start Sky
def cloudSkyTrack(task):
    task.h += globalClock.getDt() * 0.25
    if task.cloud1.isEmpty() or task.cloud2.isEmpty():
        notify.warning("Couldn't find clouds!")
        return Task.done

    task.cloud1.setH(task.h)
    task.cloud2.setH(-task.h * 0.8)
    return Task.cont

effects = CompassEffect.PRot | CompassEffect.PZ

sky = loader.loadModel('phase_3.5/models/props/TT_sky')
sky.setTransparency(TransparencyAttrib.MAlpha)
sky.setTag('sky', 'Regular')
sky.setScale(1.0)
sky.setFogOff()
sky.setDepthTest(0)
sky.setDepthWrite(0)
sky.setBin('background', 100)
sky.find('**/Sky').reparentTo(sky, -1)
sky.reparentTo(render)
sky.setZ(0.0)
sky.setHpr(0.0, 0.0, 0.0)

ce = CompassEffect.make(NodePath(), effects)
sky.node().setEffect(ce)

skyTrackTask = Task(cloudSkyTrack)
skyTrackTask.h = 0
skyTrackTask.cloud1 = sky.find('**/cloud1')
skyTrackTask.cloud2 = sky.find('**/cloud2')

if not skyTrackTask.cloud1.isEmpty() and not skyTrackTask.cloud2.isEmpty():
    taskMgr.add(skyTrackTask, 'skyTrack')

logo = OnscreenImage(
    parent=base.a2dTopCenter, image='phase_2/images/toontrocity-logo.png',
    scale=(1.15, 1.40, 0.60), pos=(0, 0, -1))
logo.setTransparency(TransparencyAttrib.MAlpha)
logo.setColorScale(Vec4(0, 0, 0, 0))

logoFade = Sequence(
    LerpColorScaleInterval(
        logo, 2, Vec4(1, 1, 1, 1), Vec4(0, 0, 0, 0),
        blendType='easeIn'),
    Wait(3),
    LerpColorScaleInterval(
        logo, 2, Vec4(0, 0, 0, 0), Vec4(1, 1, 1, 1),
        blendType='easeOut'),
)

# Spawning in random NPCs
toon = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon.setDNA(dna)
toon.reparentTo(render)
toon.setPosHpr(85, -10, 4, -15, 0, 0)
toon.animFSM.request('neutral')

toon2 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon2.setDNA(dna)
toon2.reparentTo(render)
toon2.setPosHpr(55, 10, 4, -110, 0, 0)
toon2.animFSM.request('walk')

toon3 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon3.setDNA(dna)
toon3.reparentTo(render)
toon3.setPosHpr(85, 10, 4, 75, 0, 0)
toon3.animFSM.request('neutral')

toon4 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon4.setDNA(dna)
toon4.reparentTo(render)
toon4.setPosHpr(75, 15, 4, 225, 0, 0)
toon4.animFSM.request('neutral')

toon5 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon5.setDNA(dna)
toon5.reparentTo(render)
toon5.setPosHpr(70, -15, 4, -40, 0, 0)
toon5.animFSM.request('run')

toon6 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon6.setDNA(dna)
toon6.reparentTo(render)
toon6.setPosHpr(75, -5, 4, -55, 0, 0)
toon6.animFSM.request('walk')

toon7 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon7.setDNA(dna)
toon7.reparentTo(render)
toon7.setPosHpr(62, -4, 4, 340, 0, 0)
toon7.animFSM.request('neutral')

toon8 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon8.setDNA(dna)
toon8.reparentTo(render)
toon8.setPosHpr(66, 15, 4, 225, 0, 0)
toon8.animFSM.request('neutral')

toon9 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon9.setDNA(dna)
toon9.reparentTo(render)
toon9.setPosHpr(63, -12, 4, 285, 0, 0)
toon9.animFSM.request('neutral')

toon10 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon10.setDNA(dna)
toon10.reparentTo(render)
toon10.setPosHpr(63, 2, 4, 165, 0, 0)
toon10.animFSM.request('neutral')

toon11 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon11.setDNA(dna)
toon11.reparentTo(render)
toon11.setPosHpr(52, -2, 4, 115, 0, 0)
toon11.animFSM.request('neutral')

toon12 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon12.setDNA(dna)
toon12.reparentTo(render)
toon12.setPosHpr(46, 5, 4, 220, 0, 0)
toon12.animFSM.request('neutral')

cameraPan = camera.posInterval(7, (0, 0, 20), startPos=(0, 0, 90))
fovZoom = LerpFunc(base.camLens.setFov, 20, 35, 85, 'easeOut', [], "zoom")

fovZoom2 = LerpFunc(base.camLens.setFov, 20, 85, 45, 'easeOut', [], "zoom")

walkInterval = toon2.posInterval(6, Point3(65, 5, 4), startPos=Point3(55, 10, 4))

walkInterval2 = toon6.posInterval(6, Point3(90, 10, 4), startPos=Point3(75, -5, 4))

runInterval = toon5.posInterval(5, Point3(90, 5, 4), startPos=Point3(70, -15, 4))
runIntervalSequence = Sequence(Func(runInterval.start), Wait(3), Func(toon5.animFSM.request, 'jump'), Wait(1), Func(toon5.animFSM.request, 'run'), Wait(1))

petShopCameraPosInterval = camera.posInterval(10, Point3(-93, 50, 11), startPos=Point3(-113, 65, 5))
petShopCameraHprInterval = camera.hprInterval(20, (50, -10, 0), startHpr=(50, 0, 0))
petShopCameraInterval = Sequence(Parallel(petShopCameraPosInterval, petShopCameraHprInterval))

pondCameraPosInterval = camera.posInterval(3, Point3(-90, 67, 5), startPos=Point3(-89, 99, 21))
pondCameraHprInterval = camera.hprInterval(3, (183, -10, 0), startHpr=(178, -15, 0))

pondCameraPosInterval2 = camera.posInterval(6, Point3(-84, 24, 30), startPos=Point3(-90, 67, 5))
pondCameraHprInterval2 = camera.hprInterval(6, (208, 17, 0), startHpr=(183, -10, 0))

pondCameraInterval = Sequence(Parallel(pondCameraPosInterval, pondCameraHprInterval), (Parallel(pondCameraPosInterval2, pondCameraHprInterval2)))

blimpPosInterval = blimp.posInterval(30, Point3(203, -99, 81), startPos=Point3(-2, -304, 81))
blimpHprInterval = blimp.hprInterval(20, (155, 0, 0), startHpr=(145, 0, 0))
blimpInterval = Sequence(Parallel(blimpPosInterval, blimpHprInterval))

quickZoom = LerpFunc(base.camLens.setFov, 0.2, 60, 30, 'easeIn', [], "zoom")

# base.camLens.setFov(50)

# Music for Movie
music = loader.loadMusic('phase_2/audio/bgm/toontrocity_ep1_opening.ogg')

# Sequence for Movie
movie = Sequence(
    Wait(10),
    Func(base.camera.setPosHpr, 0, 0, 90, -90, 0, 0),
    Func(base.camLens.setFov, 35),
    Func(music.play),
    Func(base.transitions.fadeOut, 0),
    Func(base.transitions.fadeIn, 4),
    Wait(3),
    Func(logoFade.start),
    Wait(4),
    Func(cameraPan.start),
    Wait(3.8),
    Func(fovZoom.start),
    Wait(3),
    Parallel(
        Func(walkInterval.start),
        Func(walkInterval2.start),
        Func(runIntervalSequence.start)),
    Wait(5),
    Parallel(
        Func(runIntervalSequence.finish),
        Func(toon5.animFSM.request, 'neutral')),
    Wait(3),
    Parallel(
        Func(fovZoom.finish),
        Func(cameraPan.finish),
        Func(petShopCameraInterval.start),
        Func(fovZoom2.start)),
    Wait(3.5),
    Func(fovZoom2.finish),
    Parallel(
        Func(petShopCameraInterval.finish),
        Func(base.camera.setPosHpr, -120, -43, 6, 145, 0, 0),
        Func(fovZoom2.start)),
    Wait(3.8),
    Func(fovZoom2.finish),
    Parallel(
        Func(base.camLens.setFov, 60),
        Func(pondCameraInterval.start)),
    Wait(4),
    Func(blimpInterval.start),
    Wait(6.3),
    Func(quickZoom.start),
    Wait(7),
    Func(base.transitions.fadeOut, 4),
    Wait(20),
    Parallel(
        Func(walkInterval.finish),
        Func(walkInterval2.finish),
        Func(runIntervalSequence.finish),
        Func(cameraPan.finish),
        Func(fovZoom.finish),
        Func(music.stop))).start()
# Tool used to get the correct camera angle
# PlacerTool3D(toon, increment=5)
# PlacerTool3D(toon2, increment=5)
# PlacerTool3D(toon3, increment=5)
# PlacerTool3D(toon4, increment=5)
# PlacerTool3D(toon5, increment=5)
# PlacerTool3D(toon6, increment=5)
# PlacerTool3D(toon7, increment=1)
# PlacerTool3D(toon8, increment=1)
# PlacerTool3D(toon9, increment=1)
# PlacerTool3D(toon10, increment=1)
# PlacerTool3D(toon11, increment=1)
# PlacerTool3D(toon12, increment=1)
# PlacerTool3D(camera, increment=1)

# base.setBackgroundColor(0,255,0)
# base.oobe()
base.run()