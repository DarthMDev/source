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
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from toontown.util.PlacerTool3D import PlacerTool3D

# Scene
scene = loader.loadModel('toontown_central_2100.bam')
scene.reparentTo(render)

# Mailbox
mailbox = Actor('phase_5/models/char/tt_r_ara_ttc_mailbox.bam',{"boost": 'phase_5/models/char/tt_a_ara_ttc_mailbox_fightBoost.bam', "idle": 'phase_5/models/char/tt_a_ara_ttc_mailbox_idle0.bam'})
mailbox.reparentTo(render)
mailbox.setPos(-309.92, -103.49, 0)

# Pie Actor
pieActor = Actor('phase_5/models/char/tt_r_prp_ext_piePackage.bam',{'fightBoost': 'phase_5/models/char/tt_a_prp_ext_piePackage_fightBoost.bam'})
pieActor.reparentTo(mailbox)

def waitForPreloading(task):
    if preloader.requests:
        return task.cont

    # Flippy
    toon = Toon.Toon()
    dna = ToonDNA.ToonDNA()
    dna.newToonFromProperties('dss', 'ms', 'm', 'm', 17, 0, 17, 17, 3, 3, 3, 3, 7, 2)
    toon.setDNA(dna)
    toon.reparentTo(render)
    #toon.setPickable(0)
    # toon.find('**/drop_shadow*').removeNode()
    toon.setPos(-303.92, -103.49, 0)
    toon.setH(180)

    pie = loader.loadModel('phase_3.5/models/props/tart.bam')
    hand = toon.find('**/rightHand')
    pie.reparentTo(hand)

    # base.camera.setPos(-303.92, -109.49, 2.5)
    # PlacerTool3D(camera, increment=0.5)

    # Create the lerp interval needed for the camera to move.
    cameraZoomInterval = camera.posInterval(1.2,
                                           Point3(-309.92, -117.49, 2.5),
                                           startPos=Point3(-304.92, -120.49, 3.5))

    cameraShiftRightInterval = camera.posInterval(0.8,
                                           Point3(-303.92, -109.49, 2.5),
                                           startPos=Point3(-309.92, -117.49, 2.5))

    # Create and play the sequence that coordinates the intervals.
    cameraPace = Sequence(cameraZoomInterval, cameraShiftRightInterval)

    base.camera.setPos(-304.92, -120.49, 3.5)

    # Movie

    toon.setPlayRate(2.25, 'throw')

    movie = Sequence(
        Wait(10),
        Parallel(
            Func(cameraPace.start),
            Func(pie.hide),
            Func(toon.play, 'bored', fromFrame=125),
            Func(mailbox.play, 'boost', fromFrame=26),
            Func(pieActor.play, 'fightBoost', fromFrame=26)),
        Wait(1.4),
        Func(pie.show),
        Func(toon.play, 'throw'),
        Wait(1.4),
        Func(pie.hide))

    sequence = Sequence(movie)
    sequence.start()

    return task.done

taskMgr.add(waitForPreloading, 'waitForPreloadingTask')

# Green Screen
base.setBackgroundColor(0,255,0)
base.run()

# TODO: Create camera pos interval to simulate the Disney version of the outro.

# DONE
# TODO: Animate mailbox and pie actor.
# TODO: Attach pie to Flippy's hand.