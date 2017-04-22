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

# The Scene our actors will play a part in
scene = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_toonhall.bam')
scene.reparentTo(render)

ropes = loader.loadModel('phase_4/models/modules/tt_m_ara_int_ropes')
ropes.reparentTo(scene)

def waitForPreloading(task):
    if preloader.requests:
        return task.cont

    # Actor Example

     # The Silly Meter
    sillyMeter = Actor('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default',
                       {'arrowTube': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_arrowFluid',
                        'phaseOne': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseOne',
                        'phaseTwo': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseTwo',
                        'phaseThree': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseThree',
                        'phaseFour': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFour',
                        'phaseFourToFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFourToFive',
                        'phaseFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFive'})
    sillyMeter.reparentTo(render)

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

    sillyMeter.loop('phaseOne', partName='meter')

    animSeq.loop()

    return task.done


taskMgr.add(waitForPreloading, 'waitForPreloadingTask')

# Green Screen

base.setBackgroundColor(0,255,0)
base.oobe()
base.run()