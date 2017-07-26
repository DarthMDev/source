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
from direct.interval.IntervalGlobal import *
from direct.filter.CommonFilters import CommonFilters
from toontown.util.PlacerTool3D import PlacerTool3D

base.camLens.setNearFar(1, 10000)

# Scene 1
toontownCentral = loader.loadModel('phase_4/models/neighborhoods/toontown_central_sz')
toontownCentral.reparentTo(render)

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
    scale=(0.75, 1, 0.40), pos=(0, 0, -0.9))
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

'''

# Spawning in random NPCs
toon = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon.setDNA(dna)
toon.reparentTo(render)
toon.setPosHpr(0, 0, 0, 0, 0, 0)
toon.animFSM.request('ScientistPlay')

toon2 = Toon.Toon()
dna = ToonDNA.ToonDNA()
dna.newToonRandom(gender=random.choice(('m', 'f')))
# dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
toon2.setDNA(dna)
toon2.reparentTo(render)
toon2.setPosHpr(0, 0, 0, 0, 0, 0)
toon2.animFSM.request('ScientistPlay')

'''

base.camLens.setFov(30)
base.camera.setPosHpr(0, 0, 90, -90, 0, 0)

cameraPan = camera.posInterval(10, (0, 0, 20), startPos=(0, 0, 90))
fovZoom = LerpFunc(base.camLens.setFov, 10, 30, 60, 'easeOut', [], "zoom")

# Sequence for Movie
movie = Sequence(
    Func(base.transitions.fadeOut, 0),
    Func(base.transitions.fadeIn, 4),
    Wait(3),
    Func(logoFade.start),
    Wait(4),
    Func(cameraPan.start),
    Wait(4),
    Func(fovZoom.start)).start()

# Tool used to get the correct camera angle
# PlacerTool3D(toon, increment=5)
# PlacerTool3D(toon2, increment=5)

# Music for Movie
music = loader.loadMusic('phase_2/audio/bgm/toontrocity_ep1_opening.ogg')
music.play()

# base.setBackgroundColor(0,255,0)
# base.oobe()
base.run()