from toontown.building.DistributedElevatorExtAI import DistributedElevatorExtAI
from toontown.strike.DistributedOperationSaveToontownAI import DistributedOperationSaveToontownAI
from toontown.strike import StrikeAreaGlobals


STRIKES = {
    StrikeAreaGlobals.STRIKE_BOSS: DistributedOperationSaveToontownAI
}


class DistributedStrikeElevatorAI(DistributedElevatorExtAI):
    def __init__(self, air, strikeLobby, strikeId):
        DistributedElevatorExtAI.__init__(self, air, strikeLobby)

        self.strikeId = strikeId

    def getStrikeId(self):
        return self.strikeId

    def generateStrike(self, avIds):
        zoneId = self.air.allocateZone()

        strike = STRIKES[self.strikeId](self.air, avIds)
        strike.generateWithRequired(zoneId)
        strike.start()

        return zoneId

    def sendAvatarsToDestination(self, avIds):
        avIds = [avId for avId in avIds if avId]

        if avIds:
            zoneId = self.generateStrike(avIds)
            for avId in avIds:
                self.sendUpdateToAvatarId(avId, 'setStrikeZone', [zoneId])

    def elevatorClosed(self):
        avIds = [avId for avId in self.seats if avId]
        if avIds:
            self.sendAvatarsToDestination(avIds)
            for seatIndex in range(len(self.seats)):
                if self.seats[seatIndex]:
                    self.clearFullNow(seatIndex)
        else:
            self.notify.warning('The Strike elevator left, but was empty.')
        self.fsm.request('closed')
