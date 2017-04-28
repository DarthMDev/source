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

# Tool used to get the correct camera angle
# PlacerTool3D(camera, increment=0.5)

# Scene 1
toontownCentral = loader.loadModel('phase_4/models/neighborhoods/toontown_central_sz')
toontownCentral.reparentTo(hidden)

sky = loader.loadModel('phase_3.5/models/props/TT_sky')
sky.reparentTo(hidden)

toonHall = toontownCentral.find('**/cityhall')
shadow = toonHall.find('**/shadow')
stoop = toonHall.find('**/stoop')

sillyMeterSignGroupA = loader.loadModel('phase_4/models/props/tt_m_ara_ttc_sillyMeterSign_groupA')
sillyMeterSignGroupA.reparentTo(hidden)
sillyMeterSignGroupA.setPosHpr(99.83, 14.77, 4, 300.96, 0, 0)

sillyMeterSignGroupB = loader.loadModel('phase_4/models/props/tt_m_ara_ttc_sillyMeterSign_groupB')
sillyMeterSignGroupB.reparentTo(hidden)
sillyMeterSignGroupB.setPosHpr(98.83, -17.25, 4, 259.51, 0, 0)

# Scene 2
toonHallInterior = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_toonhall')
toonHallInterior.reparentTo(hidden)

ropes = loader.loadModel('phase_4/models/modules/tt_m_ara_int_ropes')
ropes.reparentTo(hidden)

doorModel = loader.loadModel('phase_3.5/models/modules/doors_practical')
doorModel.reparentTo(hidden)
door = doorModel.find('**/door_double_round_ur')
door.reparentTo(hidden)
door.setPosHpr(27, -27, 0.5, -135, 0, 0)

def waitForPreloading(task):
    if preloader.requests:
        return task.cont

    # Spawning the scientists
    dimm = NPCToons.createLocalNPC(2018)
    spot1 = toonHallInterior.find('**/npc_origin_1')
    dimm.reparentTo(spot1)
    dimm.setH(180)
    dimm.reparentTo(spot1)

    sillyReader = loader.loadModel('phase_4/models/props/tt_m_prp_acs_sillyReader')
    placeholder = dimm.find('**/rightHand').attachNewNode('SillyReader')
    sillyReader.instanceTo(placeholder)
    placeholder.setH(180)
    placeholder.setScale(render, 1.0)
    placeholder.setPos(0, 0, 0.1)

    surlee = NPCToons.createLocalNPC(2019)
    spot2 = toonHallInterior.find('**/npc_origin_2')
    surlee.reparentTo(spot2)
    surlee.setH(180)

    clipBoard = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
    placeholder2 = surlee.find('**/rightHand').attachNewNode('ClipBoard')
    clipBoard.instanceTo(placeholder2)
    placeholder2.setH(180)
    placeholder2.setScale(render, 1.0)
    placeholder2.setPos(0, 0, 0.1)

    prepostera = NPCToons.createLocalNPC(2020)
    spot3 = toonHallInterior.find('**/npc_origin_3')
    prepostera.reparentTo(spot3)
    prepostera.setH(180)

    clipBoard2 = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
    placeholder3 = prepostera.find('**/rightHand').attachNewNode('ClipBoard')
    clipBoard2.instanceTo(placeholder3)
    placeholder3.setH(180)
    placeholder3.setScale(render, 1.0)
    placeholder3.setPos(0, 0, 0.1)

    # Spawning in the viewers
    # Shockley
    viewer = Toon.Toon()
    dna = ToonDNA.ToonDNA()
    dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 1, 9, 1, 9, 0, 14)
    viewer.setDNA(dna)
    viewer.setH(180)
    viewer.reparentTo(hidden)
    viewer.setPosHpr(6.5, -15.5, 0, 25, 0, 0)
    viewer.loop('neutral')

    # Roger Dog
    viewer2 = Toon.Toon()
    dna2 = ToonDNA.ToonDNA()
    dna2.newToonFromProperties('dll', 'ls', 'l', 'm', 8, 0, 8, 8, 4, 2, 4, 2, 7, 15)
    viewer2.setDNA(dna2)
    viewer2.setH(180)
    viewer2.reparentTo(hidden)
    viewer2.setPosHpr(9.5, -13.5, 0, 65, 0, 0)
    viewer2.loop('neutral')

    # Sir Max
    viewer3 = Toon.Toon()
    dna3 = ToonDNA.ToonDNA()
    dna3.newToonFromProperties('dss', 'ls', 'm', 'm', 13, 0, 13, 13, 19, 9, 13, 9, 7, 16)
    viewer3.setDNA(dna3)
    viewer3.setH(180)
    viewer3.reparentTo(hidden)
    viewer3.setPosHpr(1.5, -16.5, 0, 10, 0, 0)
    viewer3.loop('neutral')

    # Fat McStink
    viewer4 = Toon.Toon()
    dna4 = ToonDNA.ToonDNA()
    dna4.newToonFromProperties('dss', 'ms', 'm', 'm', 22, 0, 22, 22, 54, 27, 43, 27, 0, 9)
    viewer4.setDNA(dna4)
    viewer4.setH(180)
    viewer4.reparentTo(hidden)
    viewer4.setPosHpr(-2.5, -16.5, 0, 345, 0, 0)
    viewer4.loop('neutral')

    # Background actors
    randomNPC = NPCToons.createLocalNPC(4231)
    randomNPC.reparentTo(hidden)
    randomNPC.animFSM.request('neutral')
    randomNPC.setPosHpr(-6, 21, 0, 197, 0, 0)

    randomNPC2 = NPCToons.createLocalNPC(4226)
    randomNPC2.reparentTo(hidden)
    randomNPC2.animFSM.request('neutral')
    randomNPC2.setPosHpr(-2, 17, 0, 197, 0, 0)

    randomNPC3 = NPCToons.createLocalNPC(3323)
    randomNPC3.reparentTo(hidden)
    randomNPC3.animFSM.request('neutral')
    randomNPC3.setPosHpr(0, 22, 0, 183, 0, 0)

    randomNPC4 = NPCToons.createLocalNPC(1206)
    randomNPC4.reparentTo(hidden)
    randomNPC4.animFSM.request('neutral')
    randomNPC4.setPosHpr(18, 8.5, 0, 110, 0, 0)

    randomNPC5 = NPCToons.createLocalNPC(1208)
    randomNPC5.reparentTo(hidden)
    randomNPC5.animFSM.request('neutral')
    randomNPC5.setPosHpr(17, 11.5, 0, 120, 0, 0)

    randomNPC6 = NPCToons.createLocalNPC(1202)
    randomNPC6.reparentTo(hidden)
    randomNPC6.animFSM.request('neutral')
    randomNPC6.setPosHpr(15, 13.5, 0, 130, 0, 0)

    randomNPC7 = NPCToons.createLocalNPC(2016)
    randomNPC7.reparentTo(hidden)
    randomNPC7.setPos(26.943, 15.563, 0.025)
    randomNPC7.setH(45.535)

    randomNPC8 = NPCToons.createLocalNPC(5103)
    randomNPC8.reparentTo(hidden)
    randomNPC8.animFSM.request('neutral')
    randomNPC8.setPosHpr(-17, -4, 0, -90, 0, 0)

    randomNPC9 = NPCToons.createLocalNPC(2005)
    randomNPC9.reparentTo(hidden)
    randomNPC9.animFSM.request('neutral')
    randomNPC9.setPosHpr(-15.5, 13, 0, -125, 0, 0)

    randomNPC10 = NPCToons.createLocalNPC(5123)
    randomNPC10.reparentTo(hidden)
    randomNPC10.animFSM.request('neutral')
    randomNPC10.setPosHpr(-4.5, 26, 0, -172, 0, 0)

    randomNPC11 = NPCToons.createLocalNPC(3127)
    randomNPC11.reparentTo(hidden)
    randomNPC11.animFSM.request('neutral')
    randomNPC11.setPosHpr(-22.5, 2, 0, -93, 0, 0)

    randomNPC12 = NPCToons.createLocalNPC(1122)
    randomNPC12.reparentTo(hidden)
    randomNPC12.animFSM.request('neutral')
    randomNPC12.setPosHpr(-26, 8, 0, -103, 0, 0)

    randomNPC13 = NPCToons.createLocalNPC(5129)
    randomNPC13.reparentTo(hidden)
    randomNPC13.animFSM.request('neutral')
    randomNPC13.setPosHpr(-18.5, -14, 0, -63, 0, 0)

    randomNPC14 = NPCToons.createLocalNPC(3216)
    randomNPC14.reparentTo(hidden)
    randomNPC14.animFSM.request('neutral')
    randomNPC14.setPosHpr(-25, -2, 0, -93, 0, 0)

    randomNPC15 = NPCToons.createLocalNPC(5012)
    randomNPC15.reparentTo(hidden)
    randomNPC15.animFSM.request('neutral')
    randomNPC15.setPosHpr(-24.5, -9.5, 0, -71, 0, 0)

    randomNPC16 = NPCToons.createLocalNPC(3009)
    randomNPC16.reparentTo(hidden)
    randomNPC16.animFSM.request('neutral')
    randomNPC16.setPosHpr(9.5, 27.5, 0, -200, 0, 0)

    randomNPC17 = NPCToons.createLocalNPC(9226)
    randomNPC17.reparentTo(hidden)
    randomNPC17.animFSM.request('neutral')
    randomNPC17.setPosHpr(12, 15.5, 0, -205, 0, 0)

    randomNPC18 = NPCToons.createLocalNPC(4128)
    randomNPC18.reparentTo(hidden)
    randomNPC18.animFSM.request('neutral')
    randomNPC18.setPosHpr(16, 16.5, 0, -205, 0, 0)

    randomNPC19 = NPCToons.createLocalNPC(1123)
    randomNPC19.reparentTo(hidden)
    randomNPC19.animFSM.request('neutral')
    randomNPC19.setPosHpr(14, 24.5, 0, 145, 0, 0)

    randomNPC20 = NPCToons.createLocalNPC(3301)
    randomNPC20.reparentTo(hidden)
    randomNPC20.animFSM.request('neutral')
    randomNPC20.setPosHpr(4, 17.5, 0, 180, 0, 0)

    randomNPC21 = NPCToons.createLocalNPC(4007)
    randomNPC21.reparentTo(hidden)
    randomNPC21.animFSM.request('neutral')
    randomNPC21.setPosHpr(8.5, 19.5, 0, 153, 0, 0)

    randomNPC22 = NPCToons.createLocalNPC(4112)
    randomNPC22.reparentTo(hidden)
    randomNPC22.animFSM.request('neutral')
    randomNPC22.setPosHpr(-27, -6, 0, 273, 0, 0)

    randomNPC23 = NPCToons.createLocalNPC(9008)
    randomNPC23.reparentTo(hidden)
    randomNPC23.animFSM.request('neutral')
    randomNPC23.setPosHpr(-16, 21, 0, 221, 0, 0)

    randomNPC24 = NPCToons.createLocalNPC(3222)
    randomNPC24.reparentTo(hidden)
    randomNPC24.animFSM.request('neutral')
    randomNPC24.setPosHpr(-17, -7, 0, -73, 0, 0)

    randomNPC25 = NPCToons.createLocalNPC(3135)
    randomNPC25.reparentTo(hidden)
    randomNPC25.animFSM.request('neutral')
    randomNPC25.setPosHpr(-15, -11, 0, -68, 0, 0)

    randomNPC26 = NPCToons.createLocalNPC(1005)
    randomNPC26.reparentTo(hidden)
    randomNPC26.animFSM.request('neutral')
    randomNPC26.setPosHpr(4, 25.5, 0, -185, 0, 0)

    randomNPC27 = NPCToons.createLocalNPC(4137)
    randomNPC27.reparentTo(hidden)
    randomNPC27.animFSM.request('neutral')
    randomNPC27.setPosHpr(-1.817, -28.408, 0, -7.529, 0, 0)

    randomNPC28 = NPCToons.createLocalNPC(4202)
    randomNPC28.reparentTo(hidden)
    randomNPC28.animFSM.request('neutral')
    randomNPC28.setPosHpr(-14.090, -26.978, 0, -36.397, 0, 0)

    randomNPC29 = NPCToons.createLocalNPC(4007)
    randomNPC29.reparentTo(hidden)
    randomNPC29.animFSM.request('neutral')
    randomNPC29.setPosHpr(-12.073, -22.912, 0, -7.529, 0, 0)

    randomNPC30 = NPCToons.createLocalNPC(3329)
    randomNPC30.reparentTo(hidden)
    randomNPC30.animFSM.request('neutral')
    randomNPC30.setPosHpr(-2.446, -23.462, 0.025, -7.529, 0, 0)

    # Hide Nametags
    nametags3d = hidden.findAllMatches('**/nametag3d')
    nametags3d.reparentTo(hidden)

    # The Silly Meter
    sillyMeter = Actor('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default',
  {'arrowTube': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_arrowFluid',
   'phaseOne': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseOne',
   'phaseTwo': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseTwo',
   'phaseThree': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseThree',
   'phaseFour': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFour',
   'phaseFourToFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFourToFive',
   'phaseFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFive'})
    sillyMeter.reparentTo(hidden)

    smPhase1 = sillyMeter.find('**/stage1')
    smPhase2 = sillyMeter.find('**/stage2')
    smPhase3 = sillyMeter.find('**/stage3')
    smPhase4 = sillyMeter.find('**/stage4')

    smPhase2.reparentTo(hidden)
    smPhase3.reparentTo(hidden)
    smPhase4.reparentTo(hidden)

    thermometerLocator = sillyMeter.findAllMatches('**/uvj_progressBar')[1]
    thermometerMesh = sillyMeter.find('**/tube')
    thermometerMesh.setTexProjector(thermometerMesh.findTextureStage('default'), thermometerLocator, sillyMeter)
    sillyMeter.flattenMedium()
    sillyMeter.makeSubpart('arrow', ['uvj_progressBar*', 'def_springA'])
    sillyMeter.makeSubpart('meter', ['def_pivot'], ['uvj_progressBar*', 'def_springA'])

    # Arrow and fluid animations for the Silly Meter
    # Constrained, Lowest
    animSeq = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1,
                      startFrame=1, endFrame=30))

    # Moving UP from animSeq
    animSeq2 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0,
                      startFrame=31, endFrame=42))

    # Constrained
    animSeq3 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1,
                      startFrame=42, endFrame=71))

    # Moving UP from animSeq3 to the top!
    animSeq4 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0,
                      startFrame=71, endFrame=452))

    # Moving Further Up!
    animSeq5 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow',
                      constrainedLoop=0, startFrame=400, endFrame=481))

    # Heading to the Top!
    animSeq6 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow',
                      constrainedLoop=0, startFrame=441, endFrame=452))

    # The Top!
    animSeq7 = Parallel(
        ActorInterval(sillyMeter, 'arrowTube', partName='arrow',
                      constrainedLoop=1, startFrame=452, endFrame=481))

    # Toon Hall Zoom Interval
    sequenceToonHallZoom = camera.posInterval(4, (48.5, 0, 23), startPos=(42.5, 0, 26))
    sequenceToonHallZoom2 = camera.posInterval(4, (70, 13.5, 8), startPos=(65, 12.5, 8.5))

    # Background NPC Walking Interval
    walkInterval = randomNPC7.posInterval(6, Point3(13.439, 28.817, 0.025), startPos=Point3(26.943, 15.563, 0.025))

    # Prepostera Zoom Interval
    preposteraZoomInPos = camera.posInterval(1, Point3(7, -20, 3.5), startPos=Point3(6.5, -22.9, 4))
    preposteraZoomInHpr = camera.hprInterval(1, (21, 0, 0), startHpr=(17, 0, 0))
    preposteraZoomIn = Sequence(Parallel(preposteraZoomInPos, preposteraZoomInHpr))

    # Toon Hall Shake
    scaleInterval = toonHall.scaleInterval(0.1, (1, 1.2, 1.2), startScale=(1, 1, 1))
    scaleInterval2 = toonHall.scaleInterval(0.1, (1, 1, 1), startScale=(1, 1.2, 1.2))
    hprInterval = toonHall.hprInterval(0.1, (0, 9, 0), startHpr=(0, 0, 0))
    hprInterval2 = toonHall.hprInterval(0.1, (0, 0, 0), startHpr=(0, 9, 0))
    sequenceToonHallShake = Sequence(scaleInterval, scaleInterval2, hprInterval, hprInterval2)

    # Zoom Out From Scientists
    scientistZoomOut = camera.posInterval(2, Point3(0.5, -8.8, 8.5), startPos=Point3(-2.5, -1.8, 5))
    scientistZoomOut2 = camera.hprInterval(2, (-10, -15, 0), startHpr=(-35, -10, 0))
    scientistZoomOutSequence = Sequence(Parallel(scientistZoomOut, scientistZoomOut2))

    # Quick Left to Right Interval Up High Up Interval
    highPosInterval = camera.posInterval(0.6, Point3(11.5, 5, 19.5), startPos=Point3(-2, -23, 11))
    highpHprInterval = camera.hprInterval(0.6, (110, -15, 0), startHpr=(-5, 5, 0))
    highInterval = Sequence(Parallel(highPosInterval, highpHprInterval))

    # Camera Intervals spiraling up the Silly Meter Inteveral
    spiralPosInterval = camera.posInterval(1, Point3(13, -2, 9), startPos=Point3(0, -14, -2.5))
    spiralHprInterval = camera.hprInterval(1, (71, -5, 0), startHpr=(0, 40, 0))

    spiralPosInterval2 = camera.posInterval(0.5, Point3(1, 17, 12), startPos=Point3(10.5, 11.5, 11))
    spiralHprInterval2 = camera.hprInterval(0.5, (176, -5, 0), startHpr=(131, -5, 0))

    spiralPosInterval3 = camera.posInterval(0.5, Point3(-15, -5, 6.5), startPos=Point3(1, 17, 12))
    spiralHprInterval3 = camera.hprInterval(0.5, (291, 10, 0), startHpr=(176, -5, 0))

    sillyMeterSpiral = Sequence(Parallel(spiralPosInterval, spiralHprInterval))
    sillyMeterSpiral2 = Sequence(Parallel(spiralPosInterval2, spiralHprInterval2))
    sillyMeterSpiral3 = Sequence(Parallel(spiralPosInterval3, spiralHprInterval3))

    # Zoom Interval
    fovZoom = LerpFunc(base.camLens.setFov, 0.1, 90, 60, 'easeOut', [], "zoom")

    music = loader.loadMusic('phase_4/audio/bgm/ToontownSillyMeter.ogg')

    # Movie Created By Markgasus
    movie = Sequence(
        # Toon Hall,
        Parallel(
            Func(base.camera.setPos, 10000, 10000, 10000),
            Func(toontownCentral.reparentTo, render),
            Func(sky.reparentTo, render),
            Func(sillyMeterSignGroupA.reparentTo, render),
            Func(sillyMeterSignGroupB.reparentTo, render),
            Func(viewer.reparentTo, render),
            Func(viewer2.reparentTo, render),
            Func(viewer3.reparentTo, render),
            Func(viewer4.reparentTo, render),
            Func(randomNPC.reparentTo, render),
            Func(randomNPC2.reparentTo, render),
            Func(randomNPC3.reparentTo, render),
            Func(randomNPC4.reparentTo, render),
            Func(randomNPC5.reparentTo, render),
            Func(randomNPC6.reparentTo, render),
            Func(randomNPC7.reparentTo, render),
            Func(randomNPC8.reparentTo, render),
            Func(randomNPC9.reparentTo, render),
            Func(randomNPC10.reparentTo, render),
            Func(randomNPC11.reparentTo, render),
            Func(randomNPC12.reparentTo, render),
            Func(randomNPC13.reparentTo, render),
            Func(randomNPC14.reparentTo, render),
            Func(randomNPC15.reparentTo, render),
            Func(randomNPC16.reparentTo, render),
            Func(randomNPC17.reparentTo, render),
            Func(randomNPC18.reparentTo, render),
            Func(randomNPC19.reparentTo, render),
            Func(randomNPC20.reparentTo, render),
            Func(randomNPC21.reparentTo, render),
            Func(randomNPC22.reparentTo, render),
            Func(randomNPC23.reparentTo, render),
            Func(randomNPC24.reparentTo, render),
            Func(randomNPC25.reparentTo, render),
            Func(randomNPC26.reparentTo, render),
            Func(randomNPC27.reparentTo, render),
            Func(randomNPC28.reparentTo, render),
            Func(randomNPC29.reparentTo, render),
            Func(randomNPC30.reparentTo, render),
            Func(toonHallInterior.reparentTo, render),
            Func(ropes.reparentTo, render),
            Func(dimm.reparentTo, spot1),
            Func(surlee.reparentTo, spot2),
            Func(prepostera.reparentTo, spot3),
            Func(sillyMeter.reparentTo, render)),
        Wait(5),
        Parallel(
            Func(dimm.animFSM.request, 'ScientistJealous'),
            Func(surlee.animFSM.request, 'ScientistJealous'),
            Func(viewer.reparentTo, hidden),
            Func(viewer2.reparentTo, hidden),
            Func(viewer3.reparentTo, hidden),
            Func(viewer4.reparentTo, hidden),
            Func(randomNPC.reparentTo, hidden),
            Func(randomNPC2.reparentTo, hidden),
            Func(randomNPC3.reparentTo, hidden),
            Func(randomNPC4.reparentTo, hidden),
            Func(randomNPC5.reparentTo, hidden),
            Func(randomNPC6.reparentTo, hidden),
            Func(randomNPC7.reparentTo, hidden),
            Func(randomNPC8.reparentTo, hidden),
            Func(randomNPC9.reparentTo, hidden),
            Func(randomNPC10.reparentTo, hidden),
            Func(randomNPC11.reparentTo, hidden),
            Func(randomNPC12.reparentTo, hidden),
            Func(randomNPC13.reparentTo, hidden),
            Func(randomNPC14.reparentTo, hidden),
            Func(randomNPC15.reparentTo, hidden),
            Func(randomNPC16.reparentTo, hidden),
            Func(randomNPC17.reparentTo, hidden),
            Func(randomNPC18.reparentTo, hidden),
            Func(randomNPC19.reparentTo, hidden),
            Func(randomNPC20.reparentTo, hidden),
            Func(randomNPC21.reparentTo, hidden),
            Func(randomNPC22.reparentTo, hidden),
            Func(randomNPC23.reparentTo, hidden),
            Func(randomNPC24.reparentTo, hidden),
            Func(randomNPC25.reparentTo, hidden),
            Func(randomNPC26.reparentTo, hidden),
            Func(randomNPC27.reparentTo, hidden),
            Func(randomNPC28.reparentTo, hidden),
            Func(randomNPC29.reparentTo, hidden),
            Func(randomNPC30.reparentTo, hidden),
            Func(toonHallInterior.reparentTo, hidden),
            Func(ropes.reparentTo, hidden),
            Func(dimm.reparentTo, hidden),
            Func(surlee.reparentTo, hidden),
            Func(prepostera.reparentTo, hidden),
            Func(sillyMeter.reparentTo, hidden)),
        Wait(1.4),
        Parallel(
            Func(music.play),
            # Func(os.startfile, "C:/Users/Markgasus/Documents/Adobe/Premiere Pro/11.0/Toontown Rewritten Ads/Toontown Silly Meter Ad Remastered/Assets/Toontown Silly Meter.mp4"),
            Func(base.camera.setPosHpr, 42.5, 0, 26, -90, 0, 0),
            Func(sequenceToonHallZoom.start),
            Func(base.camLens.setFov, 80)),
        Wait(1.5),
            Parallel(
            Func(sequenceToonHallZoom.finish),
            Func(sequenceToonHallZoom2.start),
            Func(base.camLens.setFov, 30),
            Func(base.camera.setPos, 65, 12.5, 8.5)),
        Wait(0.80),
        Func(prepostera.animFSM.request, 'ScientistEmcee'),
        Wait(0.65),
        Parallel(Func(sequenceToonHallZoom2.finish),
            Func(base.camLens.setFov, 10),
            Func(base.camera.setPos, 52, 15.5, 6.5)),
        Wait(0.6),
        # Inside Toon Hall Camera 1
        Parallel(
            Func(dimm.reparentTo, spot1),
            Func(surlee.reparentTo, spot2),
            Func(prepostera.reparentTo, spot3),
            Func(viewer.reparentTo, hidden),
            Func(viewer2.reparentTo, hidden),
            Func(viewer3.reparentTo, hidden),
            Func(viewer4.reparentTo, hidden),
            Func(randomNPC.reparentTo, render),
            Func(randomNPC2.reparentTo, render),
            Func(randomNPC3.reparentTo, render),
            Func(randomNPC4.reparentTo, render),
            Func(randomNPC5.reparentTo, render),
            Func(randomNPC6.reparentTo, render),
            Func(randomNPC7.reparentTo, render),
            Func(randomNPC8.reparentTo, render),
            Func(randomNPC9.reparentTo, render),
            Func(randomNPC10.reparentTo, render),
            Func(randomNPC11.reparentTo, render),
            Func(randomNPC12.reparentTo, render),
            Func(randomNPC16.reparentTo, render),
            Func(randomNPC21.reparentTo, render),
            Func(randomNPC22.reparentTo, render),
            Func(randomNPC23.reparentTo, render),
            Func(sillyMeter.reparentTo, hidden),
            Func(sky.reparentTo, hidden),
            Func(toonHallInterior.reparentTo, render),
            Func(door.reparentTo, render),
            Func(ropes.reparentTo, render),
            Func(toontownCentral.reparentTo, hidden),
            Func(sillyMeterSignGroupA.reparentTo, hidden),
            Func(sillyMeterSignGroupB.reparentTo, hidden),
            Func(base.camera.setPosHpr, -0.5, 1, 3.5, -45, 0, 0),
            Func(walkInterval.start),
            Func(sillyMeter.loop, 'phaseOne', partName='meter'),
            Func(randomNPC7.loop, 'walk'),
            Func(base.camLens.setFov, 70)),
        Wait(1.9),
        Func(animSeq.loop),
        Wait(0.1),
        # Inside Toon Hall Camera 2
        Parallel(
            Func(base.camera.setPosHpr, 6.5, -22.9, 4, 17, 0, 0),
            Func(base.camLens.setFov, 90),
            Func(preposteraZoomIn.start),
            Func(prepostera.reparentTo, spot3),
            Func(viewer.reparentTo, render),
            Func(viewer2.reparentTo, render),
            Func(viewer3.reparentTo, render),
            Func(viewer4.reparentTo, render),
            Func(sillyMeter.reparentTo, render)),
        Wait(1),
        # Inside Toon Hall Camera 3
        Parallel(
            Func(preposteraZoomIn.finish),
            Func(base.camera.setPosHpr, 7, -20, 3.5, 21, 0, 0)),
        Wait(0.7),
        # Inside Toon Hall Camera 4
        Parallel(
            Func(prepostera.reparentTo, hidden),
            Func(base.camera.setPosHpr, 0, -14, -2.5, 0, 40, 0),
            Func(walkInterval.finish),
            Func(dimm.animFSM.request, 'ScientistWork'),
            Func(surlee.animFSM.request, 'ScientistWork'),
            Func(viewer.animFSM.request, 'victory'),
            Func(viewer2.animFSM.request, 'victory'),
            Func(viewer3.animFSM.request, 'victory'),
            Func(viewer4.animFSM.request, 'victory'),
            Func(surlee.animFSM.request, 'ScientistWork'),
            Func(animSeq.finish),
            Func(animSeq2.start)),
        Wait(0.4),
        Parallel(
            Func(animSeq2.finish),
            Func(animSeq3.loop)),
        Wait(1.5),
        # Inside Toon Hall Camera 5
        Parallel(
            Func(animSeq3.finish),
            Func(animSeq4.start),
            Func(randomNPC25.animFSM.request, 'victory')),
        Wait(0.1),
        Func(sillyMeterSpiral.start),
        Wait(0.9),
        Func(prepostera.reparentTo, spot3),
        Parallel(
            Func(randomNPC9.loop, 'confused'),
            Func(fovZoom.start)),
        Wait(1),
        Func(fovZoom.finish),
        Func(animSeq4.pause),
        Func(base.camera.setPos, 100, 100, 100),
        Parallel(
            Func(randomNPC.animFSM.request, 'victory'),
            Func(randomNPC2.animFSM.request, 'victory')),
        Wait(2.4),
        Func(animSeq4.resume),
        Wait(0.2),
        Parallel(
            Func(randomNPC3.animFSM.request, 'victory'),
            Func(randomNPC4.animFSM.request, 'victory'),
            Func(randomNPC5.animFSM.request, 'victory')),
        Wait(0.9),
        # Inside Toon Hall Camera 6
        Parallel(
            Func(sillyMeterSpiral2.start),
            Func(base.camLens.setFov, 70),
            Func(smPhase2.reparentTo, render),
            Func(smPhase3.reparentTo, render),
            Func(randomNPC6.animFSM.request, 'victory'),
            Func(randomNPC7.animFSM.request, 'victory'),
            Func(randomNPC8.animFSM.request, 'victory'),
            Func(randomNPC9.animFSM.request, 'victory'),
            Func(sillyMeter.loop, 'phaseThree', partName='meter')),
        Wait(0.5),
        Func(sillyMeterSpiral3.start),
        Wait(1.2),
        Func(base.camera.setPos, 100, 100, 100),
        Parallel(
            Func(randomNPC10.animFSM.request, 'victory'),
            Func(randomNPC11.animFSM.request, 'victory'),
            Func(randomNPC12.animFSM.request, 'victory'),
            Func(randomNPC13.animFSM.request, 'victory'),
            Func(randomNPC14.animFSM.request, 'victory')),
        Wait(5.5),
        Parallel(
            Func(viewer.reparentTo, hidden),
            Func(viewer2.reparentTo, hidden),
            Func(viewer3.reparentTo, hidden),
            Func(viewer4.reparentTo, hidden),
            Func(randomNPC.reparentTo, hidden),
            Func(randomNPC2.reparentTo, hidden),
            Func(randomNPC3.reparentTo, hidden),
            Func(randomNPC4.reparentTo, hidden),
            Func(randomNPC5.reparentTo, hidden),
            Func(randomNPC6.reparentTo, hidden),
            Func(randomNPC7.reparentTo, hidden),
            Func(randomNPC8.reparentTo, hidden),
            Func(randomNPC9.reparentTo, hidden),
            Func(randomNPC10.reparentTo, hidden),
            Func(randomNPC11.reparentTo, hidden),
            Func(randomNPC12.reparentTo, hidden),
            Func(randomNPC13.reparentTo, hidden),
            Func(randomNPC14.reparentTo, hidden),
            Func(randomNPC15.reparentTo, hidden),
            Func(randomNPC16.reparentTo, hidden),
            Func(randomNPC17.reparentTo, hidden),
            Func(randomNPC18.reparentTo, hidden),
            Func(randomNPC19.reparentTo, hidden),
            Func(randomNPC20.reparentTo, hidden),
            Func(randomNPC21.reparentTo, hidden),
            Func(randomNPC22.reparentTo, hidden),
            Func(randomNPC23.reparentTo, hidden),
            Func(randomNPC24.reparentTo, hidden),
            Func(randomNPC25.reparentTo, hidden),
            Func(randomNPC26.reparentTo, hidden),
            Func(randomNPC27.reparentTo, hidden),
            Func(randomNPC28.reparentTo, hidden),
            Func(randomNPC29.reparentTo, hidden),
            Func(randomNPC30.reparentTo, hidden),
            Func(toonHallInterior.reparentTo, hidden),
            Func(door.reparentTo, hidden),
            Func(sillyMeter.reparentTo, hidden),
            Func(smPhase2.reparentTo, hidden),
            Func(smPhase3.reparentTo, hidden),
            Func(ropes.reparentTo, hidden),
            Func(dimm.reparentTo, hidden),
            Func(surlee.reparentTo, hidden),
            Func(toontownCentral.reparentTo, render),
            Func(stoop.reparentTo, hidden),
            Func(shadow.reparentTo, hidden),
            Func(sillyMeterSignGroupA.reparentTo, render),
            Func(randomNPC15.animFSM.request, 'victory'),
            Func(randomNPC16.animFSM.request, 'victory'),
            Func(randomNPC17.animFSM.request, 'victory'),
            Func(randomNPC18.animFSM.request, 'victory'),
            Func(randomNPC19.animFSM.request, 'victory'),
            Func(randomNPC20.animFSM.request, 'victory'),
            Func(sillyMeterSignGroupB.reparentTo, render),
            Func(sky.reparentTo, render),
            Func(base.camera.setPosHpr, 42.5, 0, 26, -90, 0, 0),
            Func(base.camLens.setFov, 80),
            Func(sequenceToonHallZoom.start),
            Func(sequenceToonHallShake.loop),
            Func(animSeq4.pause),
            Func(dimm.animFSM.request, 'ScientistLessWork'),
            Func(surlee.animFSM.request, 'ScientistLessWork')),
        Wait(1),
        Parallel(
            Func(sequenceToonHallZoom.finish),
            Func(sequenceToonHallShake.finish),
            Func(animSeq4.resume),
            Func(base.camera.setPosHpr, 17, -16, 16, 45, -10, 0),
            Func(base.camLens.setFov, 90),
            Func(toontownCentral.reparentTo, hidden),
            Func(sky.reparentTo, hidden),
            Func(sillyMeterSignGroupA.reparentTo, hidden),
            Func(sillyMeterSignGroupB.reparentTo, hidden),
            Func(viewer.reparentTo, render),
            Func(viewer2.reparentTo, render),
            Func(viewer3.reparentTo, render),
            Func(viewer4.reparentTo, render),
            Func(randomNPC.reparentTo, render),
            Func(randomNPC2.reparentTo, render),
            Func(randomNPC3.reparentTo, render),
            Func(randomNPC4.reparentTo, render),
            Func(randomNPC5.reparentTo, render),
            Func(randomNPC6.reparentTo, render),
            Func(randomNPC7.reparentTo, render),
            Func(randomNPC8.reparentTo, render),
            Func(randomNPC9.reparentTo, render),
            Func(randomNPC10.reparentTo, render),
            Func(randomNPC11.reparentTo, render),
            Func(randomNPC12.reparentTo, render),
            Func(randomNPC13.reparentTo, render),
            Func(randomNPC14.reparentTo, render),
            Func(randomNPC15.reparentTo, render),
            Func(randomNPC16.reparentTo, render),
            Func(randomNPC17.reparentTo, render),
            Func(randomNPC18.reparentTo, render),
            Func(randomNPC19.reparentTo, render),
            Func(randomNPC20.reparentTo, render),
            Func(randomNPC21.reparentTo, render),
            Func(randomNPC22.reparentTo, render),
            Func(randomNPC23.reparentTo, render),
            Func(randomNPC24.reparentTo, render),
            Func(randomNPC25.reparentTo, render),
            Func(randomNPC26.reparentTo, render),
            Func(randomNPC27.reparentTo, render),
            Func(randomNPC28.reparentTo, render),
            Func(randomNPC29.reparentTo, render),
            Func(randomNPC30.reparentTo, render),
            Func(toonHallInterior.reparentTo, render),
            Func(ropes.reparentTo, render),
            Func(dimm.reparentTo, spot1),
            Func(surlee.reparentTo, spot2),
            Func(prepostera.reparentTo, spot3),
            Func(sillyMeter.reparentTo, render),
            Func(smPhase2.reparentTo, render),
            Func(smPhase3.reparentTo, render),
            Func(stoop.reparentTo, hidden),
            Func(shadow.reparentTo, hidden),
            Func(sillyMeter.loop, 'phaseFour', partName='meter'),
            Func(randomNPC21.animFSM.request, 'victory'),
            Func(randomNPC22.animFSM.request, 'victory'),
            Func(randomNPC23.animFSM.request, 'victory'),
            Func(randomNPC24.animFSM.request, 'victory'),
            Func(randomNPC25.animFSM.request, 'victory'),
            Func(randomNPC26.animFSM.request, 'victory'),
            Func(randomNPC27.animFSM.request, 'victory'),
            Func(randomNPC28.animFSM.request, 'victory'),
            Func(randomNPC29.animFSM.request, 'victory'),
            Func(randomNPC30.animFSM.request, 'victory')),
        Wait(0.9),
        Parallel(
            Func(base.camera.setPosHpr, -2.5, -1.8, 5, -35, -10, 0),
            Func(base.camLens.setFov, 40),
            Func(scientistZoomOutSequence.start),
            Func(smPhase2.reparentTo, hidden),
            Func(smPhase3.reparentTo, hidden),
            Func(sillyMeter.reparentTo, hidden)),
        Wait(0.9),
        Parallel(
            Func(scientistZoomOutSequence.finish),
            Func(base.camLens.setFov, 90),
            Func(base.camera.setPosHpr, -2, -23, 11, -5, 5, 0)),
        Parallel(
            Func(highInterval.start),
            Func(animSeq4.finish),
            Func(sillyMeter.reparentTo, render),
            Func(smPhase2.reparentTo, render),
            Func(smPhase3.reparentTo, render),
            Func(smPhase4.reparentTo, render),
            Func(animSeq5.start),
            Func(prepostera.reparentTo, hidden),
            Func(viewer.animFSM.request, 'victory'),
            Func(viewer.animFSM.request, 'victory'),
            Func(viewer2.animFSM.request, 'victory'),
            Func(viewer3.animFSM.request, 'victory'),
            Func(viewer4.animFSM.request, 'victory')),
        Wait(0.9),
        Parallel(
            Func(highInterval.finish),
            Func(base.camera.setPos, 100, 100, 600)),
        Wait(1.7),
        Parallel(
            Func(base.camera.setPosHpr, 0, -14, -2.5, 0, 40, 0),
            Func(animSeq5.finish),
            Func(animSeq6.start),
            Func(smPhase2.reparentTo, render),
            Func(smPhase3.reparentTo, render),
            Func(smPhase4.reparentTo, render)),
        Wait(1.7),
        Parallel(
            Func(animSeq6.finish),
            Func(animSeq7.loop)),
        Parallel(
            Func(animSeq7.finish),
            Func(base.camera.setPos, 100, 100, 100),
            Func(smPhase2.reparentTo, hidden),
            Func(smPhase3.reparentTo, hidden),
            Func(smPhase4.reparentTo, hidden),
            Func(viewer.reparentTo, hidden),
            Func(viewer2.reparentTo, hidden),
            Func(viewer3.reparentTo, hidden),
            Func(viewer4.reparentTo, hidden),
            Func(randomNPC.reparentTo, hidden),
            Func(randomNPC2.reparentTo, hidden),
            Func(randomNPC3.reparentTo, hidden),
            Func(randomNPC4.reparentTo, hidden),
            Func(randomNPC5.reparentTo, hidden),
            Func(randomNPC6.reparentTo, hidden),
            Func(randomNPC7.reparentTo, hidden),
            Func(randomNPC8.reparentTo, hidden),
            Func(randomNPC9.reparentTo, hidden),
            Func(randomNPC10.reparentTo, hidden),
            Func(randomNPC11.reparentTo, hidden),
            Func(randomNPC12.reparentTo, hidden),
            Func(randomNPC13.reparentTo, hidden),
            Func(randomNPC14.reparentTo, hidden),
            Func(randomNPC15.reparentTo, hidden),
            Func(randomNPC16.reparentTo, hidden),
            Func(randomNPC17.reparentTo, hidden),
            Func(randomNPC18.reparentTo, hidden),
            Func(randomNPC19.reparentTo, hidden),
            Func(randomNPC20.reparentTo, hidden),
            Func(randomNPC21.reparentTo, hidden),
            Func(randomNPC22.reparentTo, hidden),
            Func(randomNPC23.reparentTo, hidden),
            Func(randomNPC24.reparentTo, hidden),
            Func(randomNPC25.reparentTo, hidden),
            Func(randomNPC26.reparentTo, hidden),
            Func(randomNPC27.reparentTo, hidden),
            Func(randomNPC28.reparentTo, hidden),
            Func(randomNPC29.reparentTo, hidden),
            Func(randomNPC30.reparentTo, hidden),
            Func(toonHallInterior.reparentTo, hidden),
            Func(sillyMeter.reparentTo, hidden),
            Func(ropes.reparentTo, hidden),
            Func(dimm.reparentTo, hidden),
            Func(surlee.reparentTo, hidden),
            Func(viewer.loop, 'neutral'),
            Func(viewer2.loop, 'neutral'),
            Func(viewer3.loop, 'neutral'),
            Func(viewer4.loop, 'neutral'),
            Func(randomNPC.animFSM.request, 'neutral'),
            Func(randomNPC2.animFSM.request, 'neutral'),
            Func(randomNPC3.animFSM.request, 'neutral'),
            Func(randomNPC4.animFSM.request, 'neutral'),
            Func(randomNPC5.animFSM.request, 'neutral'),
            Func(randomNPC6.animFSM.request, 'neutral'),
            Func(randomNPC7.animFSM.request, 'neutral'),
            Func(randomNPC8.animFSM.request, 'neutral'),
            Func(randomNPC9.animFSM.request, 'neutral'),
            Func(randomNPC10.animFSM.request, 'neutral'),
            Func(randomNPC11.animFSM.request, 'neutral'),
            Func(randomNPC12.animFSM.request, 'neutral'),
            Func(randomNPC13.animFSM.request, 'neutral'),
            Func(randomNPC14.animFSM.request, 'neutral'),
            Func(randomNPC15.animFSM.request, 'neutral'),
            Func(randomNPC16.animFSM.request, 'neutral'),
            Func(randomNPC17.animFSM.request, 'neutral'),
            Func(randomNPC18.animFSM.request, 'neutral'),
            Func(randomNPC19.animFSM.request, 'neutral'),
            Func(randomNPC20.animFSM.request, 'neutral'),
            Func(randomNPC21.animFSM.request, 'neutral'),
            Func(randomNPC22.animFSM.request, 'neutral'),
            Func(randomNPC23.animFSM.request, 'neutral'),
            Func(randomNPC24.animFSM.request, 'neutral'),
            Func(randomNPC25.animFSM.request, 'neutral'),
            Func(randomNPC26.animFSM.request, 'neutral'),
            Func(randomNPC27.animFSM.request, 'neutral'),
            Func(randomNPC28.animFSM.request, 'neutral'),
            Func(randomNPC29.animFSM.request, 'neutral'),
            Func(randomNPC30.animFSM.request, 'neutral')),
        Wait(2))

    sequence = Sequence(movie)
    sequence.loop()
    # prepostera.reparentTo(render)
    # base.camera.setPosHpr(0, -10, 4.15, 0, -10, 0)
    # prepostera.animFSM.request('ScientistEmcee')
    # base.camLens.setFov(40)

    # PlacerTool3D(camera, increment=1)

    # toontownCentral.reparentTo(render)

    return task.done

taskMgr.add(waitForPreloading, 'waitForPreloadingTask')


# base.setBackgroundColor(0,255,0)
# base.oobe()
base.run()