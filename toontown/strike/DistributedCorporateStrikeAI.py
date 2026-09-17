from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject

from toontown.strike.DistributedStrikeParticipantAI import DistributedStrikeParticipantAI
from toontown.strike.StrikeWorldAI import StrikeWorldAI
from toontown.strike.StrikeBarricades import BARRICADES
from toontown.strike.DistributedStrikePowerupAI import DistributedStrikePowerupAI
from toontown.strike.DistributedStrikeHealthAI import DistributedStrikeHealthAI
from toontown.strike.DistributedStrikeAmmoStationAI import DistributedStrikeAmmoStationAI
from toontown.strike import StrikePowerupGlobals
from toontown.strike import CorporateStrikeGlobals
from toontown.toon import NPCToons


class LoadingBarrier(DirectObject):
    def __init__(self, strike, avIds, callback):
        DirectObject.__init__(self)

        self.strike = strike
        self.avIds = avIds
        self.callback = callback

        for avId in self.avIds:
            event = self.strike.air.getAvatarExitEvent(avId)
            self.acceptOnce(event, self.__handleUnexpectedExit, extraArgs=[avId])

    def remove(self, avId):
        if avId in self.avIds:
            self.avIds.remove(avId)
        self.checkDone()

    def __handleUnexpectedExit(self, avId):
        self.strike.handleUnexpectedExit(avId)
        self.avIds.remove(avId)
        self.checkDone()

    def checkDone(self):
        if len(self.avIds) == 0:
            self.callback()

    def delete(self):
        self.ignoreAll()


class DistributedCorporateStrikeAI(DistributedObjectAI, FSM):
    DROP_POINTS = []
    ROUND_MANAGER = None
    HEALTH_TREASURES = ()
    GYRO_AMMO_POS = None
    WALL_AMMO_STATIONS = ()
    BARRICADE_SPAWN_SPHERES = {}

    def __init__(self, air, avIds):
        DistributedObjectAI.__init__(self, air)
        FSM.__init__(self, 'DistributedCorporateStrikeFSM')

        self.avIds = avIds
        self.participants = []
        self.loadingBarrier = None
        self.roundManager = None
        self.world = StrikeWorldAI(self)
        self.barricadeMask = 0
        self.powerups = []
        self.healthTreasures = []
        self.ammoVendor = None
        self.ammoStations = []

    def start(self):
        self.request('Loading')

    def handleUnexpectedExit(self, avId):
        if self.state == 'Loading':
            self.avIds.remove(avId)

    def barrierDone(self):
        if self.state != 'Loading':
            return

        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'setDropPoint', self.DROP_POINTS[self.avIds.index(avId)])
        self.loadingBarrier.remove(avId)

    def enterLoading(self):
        def callback():
            self.loadingBarrier.delete()
            self.loadingBarrier = None
            self.request('Strike')

        self.loadingBarrier = LoadingBarrier(self, self.avIds[:], callback)
        self.d_setState('Loading')

    def exitLoading(self):
        pass

    def enterStrike(self):
        pIds = []

        for avId in self.avIds:
            event = self.air.getAvatarExitEvent(avId)
            self.acceptOnce(event, self.handleUnexpectedExit, extraArgs=[avId])

            p = DistributedStrikeParticipantAI(self.air, self, avId)
            self.world.registerParticipant(p)
            p.generateWithRequired(self.zoneId)
            self.participants.append(p)
            pIds.append(p.doId)

        self.d_setParticipantIds(pIds)
        self.d_setBarricadeMask()
        self._spawnHealthTreasures()
        self._spawnAmmoVendor()
        self._spawnWallAmmoStations()
        self.d_setState('Strike')
        taskMgr.doMethodLater(5, self.initalizeRounds, self.uniqueName('init-rounds'))

    def d_setState(self, state):
        self.sendUpdate('setState', [state])

    def d_setParticipantIds(self, pIds):
        self.sendUpdate('setParticipantIds', [pIds])

    def getBarricadeMask(self):
        return self.barricadeMask

    def d_setBarricadeMask(self):
        self.sendUpdate('setBarricadeMask', [self.barricadeMask])

    def requestUnlockBarricade(self, index):
        avId = self.air.getAvatarIdFromSender()
        if index < 0 or index >= len(BARRICADES):
            return
        if self.barricadeMask & (1 << index):
            return
        participant = next((p for p in self.participants if p.avId == avId), None)
        if participant is None or not participant.spendPoints(BARRICADES[index]['cost']):
            return
        self.barricadeMask |= (1 << index)
        if self.world.navigation:
            self.world.navigation.unlock(index)
        for spawnSphere in self.BARRICADE_SPAWN_SPHERES.get(index, ()):
            for strikeParticipant in self.participants:
                strikeParticipant.unlockSpawnSphere(spawnSphere)
        self._spawnHealthTreasures(index)
        self._spawnWallAmmoStations(index)
        self.d_setBarricadeMask()
        if self.roundManager:
            self.roundManager.barricadeUnlocked()

    def checkGameOver(self):
        if self.participants and all(participant.hp <= 0 for participant in self.participants):
            self.sendUpdate('gameOver', [])

    def _spawnHealthTreasures(self, unlockedBarricade=None):
        for pos, requiredBarricade in self.HEALTH_TREASURES:
            if requiredBarricade is not None and requiredBarricade != unlockedBarricade:
                continue
            if any(t.pos == pos for t in self.healthTreasures):
                continue
            treasure = DistributedStrikeHealthAI(self.air, self, pos)
            treasure.generateWithRequired(self.zoneId)
            self.healthTreasures.append(treasure)

    def _spawnAmmoVendor(self):
        if not self.GYRO_AMMO_POS or self.ammoVendor:
            return
        x, y, z, h = self.GYRO_AMMO_POS
        gyro = NPCToons.createNPC(self.air, 91925, NPCToons.NPCToonDict[91925],
                                  self.zoneId)
        gyro.strike = self
        gyro.setStrikeAmmoVendor(True)
        gyro.d_setStrikeAmmoVendor(True)
        gyro.setPos(x, y, z)
        gyro.setH(h)
        gyro.d_setPos(x, y, z)
        gyro.d_setH(h)
        self.ammoVendor = gyro

    def _spawnWallAmmoStations(self, unlockedBarricade=None):
        for posHpr, gagType, requiredBarricade in self.WALL_AMMO_STATIONS:
            if requiredBarricade is not None and requiredBarricade != unlockedBarricade:
                continue
            if any(station.posHpr == posHpr for station in self.ammoStations):
                continue
            station = DistributedStrikeAmmoStationAI(self.air, self, posHpr, gagType)
            station.generateWithRequired(self.zoneId)
            self.ammoStations.append(station)

    def spawnPowerup(self, pos):
        import random
        if random.random() > StrikePowerupGlobals.DROP_CHANCE:
            return
        powerup = DistributedStrikePowerupAI(
            self.air, self, random.choice(StrikePowerupGlobals.POWERUPS), pos)
        powerup.generateWithRequired(self.zoneId)
        self.powerups.append(powerup)

    def applyPowerup(self, participant, powerupType):
        import random
        suitType = ''
        if powerupType == StrikePowerupGlobals.MAX_AMMO:
            for strikeParticipant in self.participants:
                strikeParticipant.refillAmmo()
        elif powerupType == StrikePowerupGlobals.EMP:
            for enemy in self.roundManager.enemies[:]:
                enemy.emp()
        elif powerupType == StrikePowerupGlobals.DISGUISE:
            for strikeParticipant in (p for p in self.participants if p.hp > 0):
                strikeParticipant.activatePowerup(powerupType)
                suitType = random.choice([suit for tier in CorporateStrikeGlobals.SUIT_TIERS
                                          for suit in tier])
                self.sendUpdate('powerupCollected', [strikeParticipant.avId, powerupType,
                                                      StrikePowerupGlobals.DURATION, suitType])
            return
        else:
            participant.activatePowerup(powerupType)
        self.sendUpdate('powerupCollected', [participant.avId, powerupType,
                                              StrikePowerupGlobals.DURATION, suitType])

    def initalizeRounds(self, task):
        self.world.start()

        self.roundManager = self.ROUND_MANAGER(self)
        self.roundManager.initialize()

        self.roundManager.nextRound()
        return task.done

    def startRound(self, round):
        self.d_setRound(round)

    def d_setRound(self, round):
        self.sendUpdate('setRound', [round])
