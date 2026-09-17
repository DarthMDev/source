from toontown.building import DistributedElevator
from toontown.building.DistributedElevatorExt import DistributedElevatorExt
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.strike import StrikeAreaGlobals


class DistributedStrikeElevator(DistributedElevatorExt):
    def __init__(self, cr):
        DistributedElevatorExt.__init__(self, cr)

        self.strikeId = None

    def setStrikeId(self, strikeId):
        self.strikeId = strikeId

    def setStrikeZone(self, zoneId):
        place = self.cr.playGame.getPlace()
        requestStatus = {
            'loader': 'strike',
            'where': 'strike',
            'how': 'movie',
            'hoodId': ToontownGlobals.StrikeZoneBoss,
            'zoneId': zoneId,
            'strikeId': self.strikeId,
            'shardId': None,
            'avId': -1
        }
        elevator = self.getPlaceElevator()
        if elevator:
            elevator.signalDone(requestStatus)

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_4/models/modules/elevator')
        self.elevatorModel.setScale(1.05)
        fieldOffice = None
        hood = getattr(self.cr.playGame, 'hood', None)
        hoodLoader = getattr(hood, 'loader', None)
        if hoodLoader:
            fieldOffice = getattr(hoodLoader, 'fieldOffice', None)

        if fieldOffice and not fieldOffice.isEmpty():
            self.elevatorModel.reparentTo(fieldOffice)
            self.elevatorModel.setPosHpr(0.0, 0.0, 0.0, 180.0, 0.0, 0.0)
        else:
            self.elevatorModel.reparentTo(render)
            self.elevatorModel.setPosHpr(15.5, 28.0, 4.0, 315.0, 0.0, 0.0)
        self.leftDoor = self.elevatorModel.find('**/left-door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        self.elevatorModel.find('**/light_panel').removeNode()
        self.elevatorModel.find('**/light_panel_frame').removeNode()
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getElevatorModel(self):
        return self.elevatorModel

    def getZoneId(self):
        return 0

    def getDestName(self):
        if self.strikeId == StrikeAreaGlobals.STRIKE_BOSS:
            return TTLocalizer.StrikeZoneBoss
        return 'unknown strike id %d' % self.strikeId

    def enterWaitEmpty(self, ts):
        DistributedElevatorExt.enterWaitEmpty(self, ts)

    def exitWaitEmpty(self):
        DistributedElevatorExt.exitWaitEmpty(self)

    def enterWaitCountdown(self, ts):
        DistributedElevatorExt.enterWaitCountdown(self, ts)

    def exitWaitCountdown(self):
        DistributedElevatorExt.exitWaitCountdown(self)

    def enterClosed(self, ts):
        self.forceDoorsClosed()

    def delete(self):
        if hasattr(self, 'elevatorModel'):
            self.elevatorModel.removeNode()
            del self.elevatorModel
        DistributedElevatorExt.delete(self)
