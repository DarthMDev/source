# Boot up just a portion of the game

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


Toon.preload()

gc.enable()
gc.collect()


class ClientRepository:
    def __getattr__(self, item):
        return None


__builtin__.cr = ClientRepository()
base.cr = cr


from toontown.toon import ToonDNA
from toontown.toon import NPCToons
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *

# The Scene our actors will play a part in
scene = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_toonhall.bam')
scene.reparentTo(render)

ropes = loader.loadModel('phase_4/models/modules/tt_m_ara_int_ropes')
ropes.reparentTo(scene)


def waitForPreloading(task):
    if preloader.requests:
        return task.cont

    # Spawning a Toon through ToonDNA

    toon = Toon.Toon()
    dna = ToonDNA.ToonDNA()
    dna.newToonFromProperties('dss', 'ms', 'm', 'm', 17, 0, 17, 17, 3, 3, 3, 3, 7, 2)
    toon.setDNA(dna)
    toon.reparentTo(render)
    toon.setPickable(0)
    # toon.find('**/drop_shadow*').removeNode()
    toon.setPos(0, 0, 0)
    toon.setH(180)
    toon.hide()

    # Spawning a Toon through NPCToons

    surlee = NPCToons.createLocalNPC(2020)
    surlee.reparentTo(render)
    surlee.animFSM.request('neutral')
    surlee.setPosHpr(0, 0, 0, 0, 0, 0)

    # Spawning a Cog

    suit = Suit.Suit()
    dna = SuitDNA.SuitDNA()
    dna.newSuit('p')
    suit.setDNA(dna)
    suit.reparentTo(render)
    suit.setDisplayName('')
    suit.setPickable(0)
    suit.loop('neutral')
    # suit.pose('landing', 20)
    suit.setH(180)
    suit.find('**/drop_shadow*').removeNode()

    # Hide it's propeller if you wish to

    prop = loader.loadModel('phase_4/models/props/propeller-mod.bam')
    prop.reparentTo(suit.find('**/joint_head'))
    prop.hide()

    # Camera/Object Placement

    # base.camera.setPos(-302.92, -112.49, 2.5)
    # PlacerTool3D(camera, increment=0.5)
    # PlacerTool3D(toon, increment=0.5)

    # Create the lerp interval needed for the camera to move.
    """
    cameraZoomInterval = camera.posInterval(1.3,
                                           Point3(0, 0, 0),
                                           startPos=Point3(0, 0, 0))

    cameraInterval2 = camera.posInterval(0.7,
                                           Point3(0, 0, 0),
                                           startPos=Point3(0, 0, 0))

    # Create and play the sequence that coordinates the intervals.
    cameraPace = Sequence(cameraInterval, cameraInterval2)
    """

    """
    # Movie
    movie = Sequence(
        Wait(10),
        Parallel(
            Func(toon.hide),
            Func(pie.hide),
            Func(cameraPace.start),
            Func(mailbox.play, 'boost', fromFrame=26),
            Func(pieActor.play, 'fightBoost', fromFrame=26)),
        Wait(1.2),
        Parallel(
            Func(pie.show),
            Func(toon.show),
            Func(toon.play, 'throw', fromFrame=30)),
        Wait(1),
        Parallel(
            Func(mailbox.loop, 'idle'),
            Func(pieActor.hide)),
        Wait(0.45),
        Func(pie.hide))

    sequence = Sequence(movie)
    sequence.start()

    return task.done
    """

taskMgr.add(waitForPreloading, 'waitForPreloadingTask')

# Green Screen
base.setBackgroundColor(0,255,0)
base.oobe()
base.run()