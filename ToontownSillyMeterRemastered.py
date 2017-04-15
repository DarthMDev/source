# Boot up just a portion of Toontown

import gc
import random

gc.disable()

from pandac.PandaModules import *

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

Toon.preload()
Suit.preload()

gc.enable()
gc.collect()

class ClientRepository:
    def __getattr__(self, item):
        return None

__builtin__.cr = ClientRepository()
base.cr = cr

from toontown.toon import ToonDNA
from toontown.toon import NPCToons
from toontown.suit import SuitDNA
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *

from toontown.util.PlacerTool3D import PlacerTool3D

# The Scene our actors will play a part in
scene = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_toonhall.bam')
scene.reparentTo(render)

ropes = loader.loadModel('phase_4/models/modules/tt_m_ara_int_ropes')
ropes.reparentTo(scene)


def waitForPreloading(task):
    if preloader.requests:
        return task.cont

    # Spawning the scientists

    dimm = NPCToons.createLocalNPC(2018)
    spot1 = scene.find('**/npc_origin_1')
    dimm.reparentTo(spot1)
    dimm.animFSM.request('ScientistJealous')
    dimm.setH(180)

    sillyReader = loader.loadModel('phase_4/models/props/tt_m_prp_acs_sillyReader')
    placeholder = dimm.find('**/rightHand').attachNewNode('SillyReader')
    sillyReader.instanceTo(placeholder)
    placeholder.setH(180)
    placeholder.setScale(render, 1.0)
    placeholder.setPos(0, 0, 0.1)

    surlee = NPCToons.createLocalNPC(2019)
    spot2 = scene.find('**/npc_origin_2')
    surlee.reparentTo(spot2)
    surlee.animFSM.request('ScientistJealous')
    surlee.setH(180)

    clipBoard = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
    placeholder2 = surlee.find('**/rightHand').attachNewNode('ClipBoard')
    clipBoard.instanceTo(placeholder2)
    placeholder2.setH(180)
    placeholder2.setScale(render, 1.0)
    placeholder2.setPos(0, 0, 0.1)

    prepostera = NPCToons.createLocalNPC(2020)
    spot3 = scene.find('**/npc_origin_3')
    prepostera.reparentTo(spot3)
    prepostera.animFSM.request('ScientistEmcee')
    prepostera.setH(180)

    clipBoard2 = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
    placeholder3 = prepostera.find('**/rightHand').attachNewNode('ClipBoard')
    clipBoard2.instanceTo(placeholder3)
    placeholder3.setH(180)
    placeholder3.setScale(render, 1.0)
    placeholder3.setPos(0, 0, 0.1)

    viewer = NPCToons.createLocalNPC(3218)
    viewer.reparentTo(render)
    viewer.animFSM.request('neutral')
    viewer.setH(180)
    viewer.setPosHpr(6.5, -15.5, 0, 25, 0, 0)

    viewer2 = NPCToons.createLocalNPC(3302)
    viewer2.reparentTo(render)
    viewer2.animFSM.request('neutral')
    viewer2.setH(180)
    viewer2.setPosHpr(9.5, -13.5, 0, 65, 0, 0)

    viewer3 = NPCToons.createLocalNPC(1314)
    viewer3.reparentTo(render)
    viewer3.animFSM.request('neutral')
    viewer3.setH(180)
    viewer3.setPosHpr(1.5, -16.5, 0, 10, 0, 0)

    viewer4 = NPCToons.createLocalNPC(2011)
    viewer4.reparentTo(render)
    viewer4.animFSM.request('neutral')
    viewer4.setH(180)
    viewer4.setPosHpr(-2.5, -16.5, 0, 345, 0, 0)

    # Blue Lou: 6.5, -15.5, 0, 25, 0, 0
    # Sid: 9.5, -13.5, 0, 65, 0, 0
    # Ralph: 1.5, -16.5, 0, 10, 0, 0
    # Porter: -2.5, -16.5, 0, 345, 0, 0

    # The Silly Meter

    sillyMeter = Actor('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default',
  {'arrowTube': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_arrowFluid',
   'phaseOne': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseOne',
   'phaseTwo': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseTwo',
   'phaseThree': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseThree',
   'phaseFour': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFour',
   'phaseFourToFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFourToFive',
   'phaseFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFive'})
    sillyMeter.reparentTo(scene)

    smPhase1 = sillyMeter.find('**/stage1')
    smPhase2 = sillyMeter.find('**/stage2')
    smPhase3 = sillyMeter.find('**/stage3')
    smPhase4 = sillyMeter.find('**/stage4')
    smPhase2.hide()
    smPhase3.hide()
    smPhase4.hide()

    thermometerLocator = sillyMeter.findAllMatches('**/uvj_progressBar')[1]
    thermometerMesh = sillyMeter.find('**/tube')
    thermometerMesh.setTexProjector(thermometerMesh.findTextureStage('default'), thermometerLocator, sillyMeter)
    sillyMeter.flattenMedium()
    sillyMeter.makeSubpart('arrow', ['uvj_progressBar*', 'def_springA'])
    sillyMeter.makeSubpart('meter', ['def_pivot'], ['uvj_progressBar*', 'def_springA'])

    animSeq = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1,
                      startFrame=1, endFrame=30))
    animSeq.start()
    animSeq.loop()
    sillyMeter.loop('phaseOne', partName='meter')

    # Camera/Object Placement

    # base.oobe()

    # Surlee and Dimm Camera Position
    # base.camera.setPosHpr(-0.5, 1, 3.5, -45, 0, 0)

    # Prepostera telling Toons about Silly Meter
    base.camera.setPosHpr(6.5, -22, 4, 15, 0, 0)

    # Tool used to get the correct camera angle

    # PlacerTool3D(camera, increment=0.1)
    # PlacerTool3D(viewer2, increment=0.5)
    # PlacerTool3D(viewer3, increment=0.5)
    # PlacerTool3D(viewer4, increment=0.5)

    # Set FOV to get enhanced shots
    base.camLens.setFov(100)

    # Create the lerp interval needed for the camera to move.
    cameraZoomInterval = camera.posInterval(1.3,
                                           Point3(0, 0, 0),
                                           startPos=Point3(0, 0, 0))

    cameraInterval2 = camera.posInterval(0.7,
                                           Point3(0, 0, 0),
                                           startPos=Point3(0, 0, 0))

    # Create and play the sequence that coordinates the intervals.
    # cameraPace = Sequence(cameraInterval, cameraInterval2)

    # Surlee and Dimm Alone Movie
    movie = Sequence(
        Func(dimm.hide),
        Func(surlee.hide),
        Wait(5),
        Parallel(
            Func(dimm.show),
            Func(surlee.show),
            Func(dimm.animFSM.request, 'ScientistJealous'),
            Func(surlee.animFSM.request, 'ScientistJealous')))

    # sequence = Sequence(movie)
    # sequence.start()

    # Green Screen
    base.setBackgroundColor(0, 255, 0)

    return task.done

taskMgr.add(waitForPreloading, 'waitForPreloadingTask')

base.run()