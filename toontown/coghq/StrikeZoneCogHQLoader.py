from direct.actor import Actor
from toontown.coghq import CogHQLoader
from toontown.coghq import StrikeZoneCogHQExterior
from toontown.coghq import StrikeZoneHQBossBattle


class StrikeZoneCogHQLoader(CogHQLoader.CogHQLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSM, doneEvent)
        self.musicFile = 'phase_4/audio/corpstrike/GOV_strikezone_nbrhood.ogg'
        self.cogHQExteriorModelPath = 'phase_4/models/corpstrike/toontown_central_strike_zone'
        self.buildings = []
        self.props = []
        self.fieldOffice = None
        self.geom = None

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        self.battleMusic = base.loadMusic('phase_4/audio/corpstrike/cs_ost_bgm_1.ogg')

    def loadPlaceGeom(self, zoneId):
        self.geom = loader.loadModel(self.cogHQExteriorModelPath)
        self.geom.setHpr(-90, 0, 0)

        self.toonHall = loader.loadModel('phase_4/models/corpstrike/destroyed_toonhall')
        self.toonHall.reparentTo(render)
        self.toonHall.setPosHpr(116.66, 24.29, 4, -90, 0, 0)

        self.bank = loader.loadModel('phase_4/models/corpstrike/destroyed_bank')
        self.bank.reparentTo(render)
        self.bank.setPos(57.1796, 38.6656, 0.3)

        self.library = loader.loadModel('phase_4/models/corpstrike/destroyed_library')
        self.library.reparentTo(render)
        self.library.setPosHpr(91.4475, -44.9255, 4, 180, 0, 0)

        self.toonHQ = loader.loadModel('phase_4/models/corpstrike/hqTT_ost')
        self.toonHQ.reparentTo(render)
        self.toonHQ.setPosHpr(23.6425, 24.8587, 4, 135, 0, 0)

        try:
            self.hqTelescope = Actor.Actor('phase_4/models/corpstrike/hqTT_telescope_ost', {'animation': 'phase_4/models/corpstrike/hqTT_telescope_ost'})
        except:
            self.hqTelescope = Actor.Actor('phase_4/models/corpstrike/excited_telescope', {'animation': 'phase_4/models/corpstrike/excited_telescope'})
        self.hqTelescope.loop('animation')
        self.hqTelescope.reparentTo(render)
        self.hqTelescope.setPosHpr(20.5, 29, 16.7, -70, 0, 0)

        try:
            self.gazebo = loader.loadModel('phase_4/models/corpstrike/gazebo_ost')
        except:
            self.gazebo = loader.loadModel('phase_4/models/modules/gazebo')
        if self.gazebo:
            self.gazebo.reparentTo(render)
            self.gazebo.setPosHpr(-60.94, -8.8, -2, -178, 0, 0)

        self.tunnel = loader.loadModel('phase_4/models/corpstrike/safe_zone_tunnel_TT_ost')
        self.tunnel.reparentTo(render)
        self.tunnel.setPosHpr(-239.67, 64.08, -6.18, -90, 0, 0)

        self.tunnel2 = loader.loadModel('phase_4/models/corpstrike/safe_zone_tunnel_TT_ost')
        self.tunnel2.reparentTo(render)
        self.tunnel2.setPosHpr(-68.38, -202.64, -3.58, -31, 0, 0)

        self.tunnel3 = loader.loadModel('phase_4/models/corpstrike/safe_zone_tunnel_TT_ost')
        self.tunnel3.reparentTo(render)
        self.tunnel3.setPosHpr(27.6402, 176.475, -6.18, 171, 0, 0)

        try:
            self.streetLight = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        except:
            self.streetLight = loader.loadModel('phase_3.5/models/props/streetlight_TT')

        oneLightNode = self.streetLight.find('**/prop_post_one_light')
        threeLightNode = self.streetLight.find('**/prop_post_three_light')

        self.oneLight = oneLightNode.copyTo(render)
        self.oneLight.setPosHpr(3.84337, 118.504, 3, -110, 0, 0)

        self.oneLight2 = oneLightNode.copyTo(render)
        self.oneLight2.setPosHpr(116.979, 146.926, 3, 145, 0, 0)

        self.oneLight3 = oneLightNode.copyTo(render)
        self.oneLight3.setPosHpr(86.808, 164.831, 3, -95, 0, 0)

        self.threeLight = threeLightNode.copyTo(render)
        self.threeLight.setPosHpr(46.7488, -86.2016, 3.00007, -2, 0, 0)

        self.threeLight2 = threeLightNode.copyTo(render)
        self.threeLight2.setPosHpr(77.3059, -86.4255, 2.9999, -2, 0, 0)

        self.threeLight3 = threeLightNode.copyTo(render)
        self.threeLight3.setPosHpr(58.8052, 92.6999, 3, -90, 0, 0)

        self.threeLight4 = threeLightNode.copyTo(render)
        self.threeLight4.setPosHpr(94.8051, 92.6997, 3, -90, 0, 0)

        self.oneLight4 = oneLightNode.copyTo(render)
        self.oneLight4.setPosHpr(134.882, -125.532, 3, -130, 0, 0)

        self.oneLight5 = oneLightNode.copyTo(render)
        self.oneLight5.setPosHpr(4.9912, -116.182, 3, -155, 0, 0)

        self.threeLight5 = threeLightNode.copyTo(render)
        self.threeLight5.setPosHpr(108.962, -28.0532, 4, -180, 0, 0)

        self.threeLight6 = threeLightNode.copyTo(render)
        self.threeLight6.setPosHpr(108.205, 32.0659, 4, -180, 0, 0)

        self.threeLight7 = threeLightNode.copyTo(render)
        self.threeLight7.setPosHpr(32.9609, 61.9462, 4, 180, 0, 0)

        self.threeLight8 = threeLightNode.copyTo(render)
        self.threeLight8.setPosHpr(28.9617, -57.0532, 4, 180, 0, 0)

        self.threeLight9 = threeLightNode.copyTo(render)
        self.threeLight9.setPosHpr(-99.98, -66.4832, 0.5, 175, 0, 0)

        self.threeLight10 = threeLightNode.copyTo(render)
        self.threeLight10.setPosHpr(-125.889, -42.5582, 0.5, 175, 0, 0)

        self.oneLight6 = oneLightNode.copyTo(render)
        self.oneLight6.setPosHpr(-125, 60, 0.525, 52, 0, 0)

        try:
            self.fieldOffice = loader.loadModel('phase_4/models/corpstrike/tt_m_ara_cbe_fieldOfficePhilip_full')
        except:
            self.fieldOffice = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_fieldOfficeMoverShaker')
        if self.fieldOffice:
            self.fieldOffice.reparentTo(render)
            self.fieldOffice.setPosHpr(0, 0, 0, 0, 0, 0)
            self.buildings.append(self.fieldOffice)

        self.buildings.append(self.toonHall)
        self.buildings.append(self.bank)
        self.buildings.append(self.library)
        self.buildings.append(self.toonHQ)
        self.props.append(self.hqTelescope)
        if self.gazebo:
            self.props.append(self.gazebo)
        self.props.append(self.tunnel)
        self.props.append(self.tunnel2)
        self.props.append(self.tunnel3)

        self.props.append(self.oneLight)
        self.props.append(self.oneLight2)
        self.props.append(self.oneLight3)
        self.props.append(self.oneLight4)
        self.props.append(self.oneLight5)
        self.props.append(self.oneLight6)
        self.props.append(self.threeLight)
        self.props.append(self.threeLight2)
        self.props.append(self.threeLight3)
        self.props.append(self.threeLight4)
        self.props.append(self.threeLight5)
        self.props.append(self.threeLight6)
        self.props.append(self.threeLight7)
        self.props.append(self.threeLight8)
        self.props.append(self.threeLight9)
        self.props.append(self.threeLight10)

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        for building in self.buildings:
            building.removeNode()
        for prop in self.props:
            prop.removeNode()
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)

    def getExteriorPlaceClass(self):
        return StrikeZoneCogHQExterior.StrikeZoneCogHQExterior

    def getBossPlaceClass(self):
        return StrikeZoneHQBossBattle.SZHQBossBattle
