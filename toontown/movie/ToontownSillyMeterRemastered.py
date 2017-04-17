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
scene.hide()

ropes = loader.loadModel('phase_4/models/modules/tt_m_ara_int_ropes')
ropes.reparentTo(scene)
ropes.hide()

toontownCentral = loader.loadModel('phase_4/models/neighborhoods/toontown_central_sz')
toontownCentral.reparentTo(render)
toonHall = toontownCentral.find('**/cityhall')
# toonHall.find('**/shadow').hide()
# toonHall.find('**/stoop').hide()

sillyMeterSignGroupA = loader.loadModel('phase_4/models/props/tt_m_ara_ttc_sillyMeterSign_groupA')
sillyMeterSignGroupA.reparentTo(render)
sillyMeterSignGroupA.setPosHpr(99.83, 11.67, 4, 300.96, 0, 0)

sillyMeterSignGroupB = loader.loadModel('phase_4/models/props/tt_m_ara_ttc_sillyMeterSign_groupB')
sillyMeterSignGroupB.reparentTo(render)
sillyMeterSignGroupB.setPosHpr(98.83, -17.25, 4, 259.51, 0, 0)

scaleInterval = toonHall.scaleInterval(0.1, (1, 1.2, 1.2), startScale=(1, 1, 1))
scaleInterval2 = toonHall.scaleInterval(0.1, (1, 1, 1), startScale=(1, 1.2, 1.2))

hprInterval = toonHall.hprInterval(0.1, (0, 9, 0), startHpr=(0, 0, 0))
hprInterval2 = toonHall.hprInterval(0.1, (0, 0, 0), startHpr=(0, 9, 0))

PlacerTool3D(camera, increment=0.5)

base.camera.setPosHpr(43.5, 0, 25, -90, 0, 0)
base.camLens.setFov(90)


# sequenceToonHall = Sequence(scaleInterval, scaleInterval2, hprInterval, hprInterval2)
# sequenceToonHall.loop()

def waitForPreloading(task):
    if preloader.requests:
        return task.cont
    # Spawning the scientists

    dimm = NPCToons.createLocalNPC(2018)
    spot1 = scene.find('**/npc_origin_1')
    dimm.reparentTo(spot1)
    dimm.setH(180)
    dimm.hide()

    sillyReader = loader.loadModel('phase_4/models/props/tt_m_prp_acs_sillyReader')
    placeholder = dimm.find('**/rightHand').attachNewNode('SillyReader')
    sillyReader.instanceTo(placeholder)
    placeholder.setH(180)
    placeholder.setScale(render, 1.0)
    placeholder.setPos(0, 0, 0.1)
    sillyReader.hide()

    surlee = NPCToons.createLocalNPC(2019)
    spot2 = scene.find('**/npc_origin_2')
    surlee.reparentTo(spot2)
    surlee.setH(180)
    surlee.hide()

    clipBoard = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
    placeholder2 = surlee.find('**/rightHand').attachNewNode('ClipBoard')
    clipBoard.instanceTo(placeholder2)
    placeholder2.setH(180)
    placeholder2.setScale(render, 1.0)
    placeholder2.setPos(0, 0, 0.1)

    prepostera = NPCToons.createLocalNPC(2020)
    spot3 = scene.find('**/npc_origin_3')
    prepostera.reparentTo(spot3)
    prepostera.setH(180)
    prepostera.hide()

    clipBoard2 = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
    placeholder3 = prepostera.find('**/rightHand').attachNewNode('ClipBoard')
    clipBoard2.instanceTo(placeholder3)
    placeholder3.setH(180)
    placeholder3.setScale(render, 1.0)
    placeholder3.setPos(0, 0, 0.1)

    # Shockley
    viewer = Toon.Toon()
    dna = ToonDNA.ToonDNA()
    dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
    viewer.setDNA(dna)
    viewer.setH(180)
    viewer.reparentTo(render)
    viewer.setPosHpr(6.5, -15.5, 0, 25, 0, 0)
    viewer.loop('neutral')
    viewer.hide()

    # Roger Dog
    viewer2 = Toon.Toon()
    dna2 = ToonDNA.ToonDNA()
    dna2.newToonFromProperties('dll', 'ls', 'l', 'm', 8, 0, 8, 8, 4, 2, 4, 2, 7, 15)
    viewer2.setDNA(dna2)
    viewer2.setH(180)
    viewer2.reparentTo(render)
    viewer2.setPosHpr(9.5, -13.5, 0, 65, 0, 0)
    viewer2.loop('neutral')
    viewer2.hide()

    # Sir Max
    viewer3 = Toon.Toon()
    dna3 = ToonDNA.ToonDNA()
    dna3.newToonFromProperties('dss', 'ls', 'm', 'm', 13, 0, 13, 13, 19, 9, 13, 9, 7, 16)
    viewer3.setDNA(dna3)
    viewer3.setH(180)
    viewer3.reparentTo(render)
    viewer3.setPosHpr(1.5, -16.5, 0, 10, 0, 0)
    viewer3.loop('neutral')
    viewer3.hide()

    # Fat McStink
    viewer4 = Toon.Toon()
    dna4 = ToonDNA.ToonDNA()
    dna4.newToonFromProperties('dss', 'ms', 'm', 'm', 22, 0, 22, 22, 54, 27, 43, 27, 0, 9)
    viewer4.setDNA(dna4)
    viewer4.setH(180)
    viewer4.reparentTo(render)
    viewer4.setPosHpr(-2.5, -16.5, 0, 345, 0, 0)
    viewer4.loop('neutral')
    viewer4.hide()

    randomNPC = NPCToons.createLocalNPC(2016)
    randomNPC.reparentTo(render)
    randomNPC.setPos(17, -9.5, 0)
    randomNPC.setH(-5)
    randomNPC.hide()

    randomNPC2 = NPCToons.createLocalNPC(5103)
    randomNPC2.reparentTo(render)
    randomNPC2.animFSM.request('neutral')
    randomNPC2.setPosHpr(-17, -4, 0, -90, 0, 0)
    randomNPC2.hide()

    randomNPC3 = NPCToons.createLocalNPC(2005)
    randomNPC3.reparentTo(render)
    randomNPC3.animFSM.request('neutral')
    randomNPC3.setPosHpr(-14.5, 8.5, 0, -130, 0, 0)
    randomNPC3.hide()

    flippy = Toon.Toon()
    dna = ToonDNA.ToonDNA()
    dna.newToonFromProperties('dss', 'ms', 'm', 'm', 17, 0, 17, 17, 3, 3, 3, 3, 7, 2)
    flippy.setDNA(dna)
    flippy.reparentTo(render)
    flippy.hide()
    flippy.setPickable(0)
    flippy.loop('neutral')
    flippy.find('**/drop_shadow*').removeNode()
    flippy.setPosHpr(9, 5.5, 0, 135, 0, 0)
    pie = loader.loadModel('phase_3.5/models/props/tart.bam')
    hand = flippy.find('**/rightHand')
    pie.reparentTo(hand)

    # Background NPC Walking Interval
    posInterval = randomNPC.posInterval(10, Point3(17, 17.5, 0), startPos=Point3(17, -9.5, 0))

    # Next Location
    posInterval2 = randomNPC.posInterval(5, Point3(17, 28.5, 0), startPos=Point3(17, 17.5, 0))

    # Final Location
    posInterval3 = randomNPC.posInterval(5, Point3(17, 38.5, 0), startPos=Point3(17, 28.5, 0))

    posPace = Sequence(posInterval)
    posPace2 = Sequence(posInterval2, posInterval3)

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

    thermometerLocator = sillyMeter.findAllMatches('**/uvj_progressBar')[1]
    thermometerMesh = sillyMeter.find('**/tube')
    thermometerMesh.setTexProjector(thermometerMesh.findTextureStage('default'), thermometerLocator, sillyMeter)
    sillyMeter.flattenMedium()
    sillyMeter.makeSubpart('arrow', ['uvj_progressBar*', 'def_springA'])
    sillyMeter.makeSubpart('meter', ['def_pivot'], ['uvj_progressBar*', 'def_springA'])

    # Arrow and fluid animations

    # Constrained, Lowest
    animSeq = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1,
                      startFrame=1, endFrame=30))

    # Moving UP from animSeq
    animSeq2 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0,
                      startFrame=31, endFrame=42))

    # Constrained, Completion of animSeq
    animSeq3 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1,
                      startFrame=42, endFrame=71))

    # Moving UP from animSeq3
    animSeq4 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0,
                      startFrame=71, endFrame=240))

    # To the top!
    animSeq5 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0,
                      startFrame=420, endFrame=452))

    # Tool used to get the correct camera angle
    # PlacerTool3D(camera, increment=0.5)
    # PlacerTool3D(randomNPC3, increment=0.5)
    # PlacerTool3D(viewer3, increment=0.5)
    # PlacerTool3D(viewer4, increment=0.5)

    # Movie
    movie = Sequence(
        # Prepare Movie
        Func(base.camera.setPosHpr, -0.5, 1, 3.5, -45, 0, 0),
        Func(smPhase2.hide),
        Func(smPhase3.hide),
        Func(smPhase4.hide),
        Func(dimm.hide),
        Func(surlee.hide),
        Func(prepostera.hide),
        Func(viewer.hide),
        Func(viewer2.hide),
        Func(viewer3.hide),
        Func(viewer4.hide),
        Func(randomNPC.hide),
        Func(randomNPC2.hide),
        Func(randomNPC3.hide),
        # Start Movie
        # Camera 1
        Parallel(
            Func(dimm.show),
            Func(surlee.show),
            Func(dimm.animFSM.request, 'ScientistJealous'),
            Func(surlee.animFSM.request, 'ScientistJealous')),
        Wait(8),
        Func(base.camera.setPosHpr, 6.5, -22, 4, 15, 0, 0),
        Func(base.camLens.setFov, 110),
        Func(dimm.show),
        Func(surlee.show),
        Func(prepostera.show),
        Func(viewer.show),
        Func(viewer2.show),
        Func(viewer3.show),
        Func(viewer4.show),
        Func(randomNPC.show),
        Func(randomNPC2.show),
        Func(randomNPC3.show),
        # Camera 2
        Parallel(
            Func(randomNPC.loop, 'walk'),
            Func(posPace.start),
            Func(prepostera.animFSM.request, 'ScientistEmcee'),
            Func(dimm.animFSM.request, 'ScientistJealous'),
            Func(surlee.animFSM.request, 'ScientistJealous'),
            Func(sillyMeter.loop, 'phaseOne', partName='meter'),
            Func(animSeq.loop)),
        Wait(4),
        # Camera 3
        Parallel(
            Func(viewer.hide),
            Func(viewer2.hide),
            Func(viewer3.hide),
            Func(viewer4.hide),
            Func(base.camera.setPosHpr, 5.8, -18.3, 3, 15, 0, 0)),
        Wait(1),
        # Camera 4
        Parallel(
            Func(base.camera.setPosHpr, 0, -12.5, 1, 0, 30, 0),
            Func(base.camLens.setFov, 110),
            Func(animSeq.finish),
            Func(animSeq2.start),
            Func(posPace2.start),
            Func(dimm.show),
            Func(surlee.show),
            Func(prepostera.animFSM.request, 'ScientistEmcee'),
            Func(randomNPC.show),
            Func(randomNPC3.show),
            Func(dimm.animFSM.request, 'ScientistWork'),
            Func(surlee.animFSM.request, 'ScientistWork'),
            Func(randomNPC.loop, 'walk')),
        Wait(0.5),
        Func(animSeq3.loop),
        Wait(3),
        Func(animSeq3.finish),
        Func(base.camLens.setFov, 50),
        Func(base.camera.setPosHpr, 25, 16.5, 1, 124, 10, 0),
        Parallel(
            Func(viewer3.show),
            Func(viewer4.show),
            Func(animSeq4.start),
            Func(animSeq4.loop)),
        Wait(0.8),
        Func(randomNPC3.loop, 'confused'))

    # sequence = Sequence(movie)
    # sequence.start()

    cameraShiftRightInterval = camera.posInterval(0.6,
                                           Point3(0.7, -2.6, 2.5),
                                           startPos=Point3(-3.1, 1.2, 2.5))
    # Ending
    movie4 = Sequence(
        # Prepare Movie
        Func(base.camera.setPosHpr, 0, -12.5, 1, 0, 30, 0),
        Func(animSeq5.start),
        Func(dimm.animFSM.request, 'ScientistLessWork'),
        Func(surlee.animFSM.request, 'ScientistLessWork'),
        Func(base.camLens.setFov, 110),
        Wait(2),
        Parallel(
            Func(base.camera.setPosHpr, -3.1, 1.2, 2.5, -45, 0, 0),
            Func(base.camLens.setFov, 35),
            Func(flippy.hide),
            Func(pie.hide),
            Func(surlee.hide),
            Func(dimm.hide),
            Func(surlee.show),
            Func(dimm.show)),
        Wait(0.5),
        Parallel(
            Func(cameraShiftRightInterval.start),
            Func(pie.show),
            Func(sillyMeter.hide),
            Func(flippy.show),
            Func(flippy.play, 'throw', fromFrame=28)))

    # sequence4 = Sequence(movie4)
    # sequence4.start()

    # Green Screen
    # base.setBackgroundColor(0, 255, 0)

    return task.done

taskMgr.add(waitForPreloading, 'waitForPreloadingTask')

# base.oobe()
base.run()