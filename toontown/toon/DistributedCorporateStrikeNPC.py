from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from toontown.toon import ToonHead
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from toontown.strike import CorporateStrikeGlobals
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout


class DistributedCorporateStrikeNPC(DistributedNPCToonBase):
    DISPATCH_MESSAGE = (
        'The Resistance needs your help in ruined Toontown Central! '
        'You can meet your friends at the Strike elevator once you arrive.')
    GYRO_MESSAGE = (
        'Greetings, %s! I am Gyro Gearloose. Keep those Cogs busy, '
        'and I will keep working on our Strike defenses!')

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.dispatchDialog = None
        self.strikeAmmoVendor = False

    def setStrikeAmmoVendor(self, value):
        self.strikeAmmoVendor = bool(value)

    def generateToonHead(self, copy=1):
        if not self._isGyro():
            return DistributedNPCToonBase.generateToonHead(self, copy)
        originalHead = ToonHead.HeadDict['f']
        originalLashes = ToonHead.EyelashDict['f']
        ToonHead.HeadDict['f'] = '/models/char/gyro-heads-'
        ToonHead.EyelashDict['f'] = '/models/char/gyro-lashes'
        try:
            return DistributedNPCToonBase.generateToonHead(self, copy)
        finally:
            ToonHead.HeadDict['f'] = originalHead
            ToonHead.EyelashDict['f'] = originalLashes

    def generateToon(self):
        DistributedNPCToonBase.generateToon(self)
        self._applyGyroClothes()

    def generateToonClothes(self, fromNet=0):
        result = DistributedNPCToonBase.generateToonClothes(self, fromNet)
        self._applyGyroClothes()
        return result

    def _applyGyroClothes(self):
        if not self._isGyro() or not self.hasLOD():
            return
        shirt = loader.loadTexture('phase_3/maps/gyro-shirt.png')
        sleeves = loader.loadTexture('phase_3/maps/gyro-sleeve.png')
        shorts = loader.loadTexture('phase_3/maps/gyro-shorts.png')
        for lodName in self.getLODNames():
            torso = self.getPart('torso', lodName)
            torso.find('**/torso-top').setTexture(shirt, 1)
            torso.find('**/sleeves').setTexture(sleeves, 1)
            for bottom in torso.findAllMatches('**/torso-bot'):
                bottom.setTexture(shorts, 1)

    def _isGyro(self):
        return bool(getattr(self, 'style', None) and
                    self.style.getAnimal() == 'duck')

    def disable(self):
        self._cleanupDispatchDialog()
        DistributedNPCToonBase.disable(self)

    def handleCollisionSphereEnter(self, collEntry):
        if self.dispatchDialog:
            return
        if self.strikeAmmoVendor:
            self.dispatchDialog = TTDialog.TTDialog(
                text=('I can refill every Strike gag for %s points.\n'
                      'Want a fresh supply?' %
                      CorporateStrikeGlobals.GYRO_AMMO_REFILL_COST),
                style=TTDialog.TwoChoice,
                buttonTextList=['Refill', TTLocalizer.lCancel],
                command=self._handleAmmoChoice)
            self.dispatchDialog.show()
            return
        if self._isGyro():
            self.setChatAbsolute(self.GYRO_MESSAGE % base.localAvatar.getName(),
                                 CFSpeech | CFTimeout)
            return
        self.dispatchDialog = TTDialog.TTDialog(
            text=self.DISPATCH_MESSAGE,
            style=TTDialog.TwoChoice,
            buttonTextList=['Enter', TTLocalizer.lCancel],
            command=self._handleDispatchChoice)
        self.dispatchDialog.show()

    def _handleDispatchChoice(self, choice):
        self._cleanupDispatchDialog()
        if choice == 1:
            self.sendUpdate('requestEnterStrikeZone', [])

    def _handleAmmoChoice(self, choice):
        self._cleanupDispatchDialog()
        if choice == 1:
            self.sendUpdate('requestStrikeAmmoRefill', [])

    def strikeAmmoPurchaseResult(self, success):
        text = ('All Strike gags refilled!' if success else
                'You need 500 points, or your gags are already full.')
        self.dispatchDialog = TTDialog.TTDialog(
            text=text, style=TTDialog.Acknowledge,
            command=lambda ignored: self._cleanupDispatchDialog())
        self.dispatchDialog.show()

    def enterStrikeZone(self):
        if base.localAvatar.hasActiveBoardingGroup():
            base.localAvatar.elevatorNotifier.showMe(
                TTLocalizer.BoardingCannotLeaveZone)
            return

        place = base.cr.playGame.getPlace()
        if place:
            place.requestLeave({
                'loader': 'cogHQLoader',
                'where': 'cogHQExterior',
                'how': 'teleportIn',
                'hoodId': 19000,
                'zoneId': 19000,
                'shardId': None,
                'avId': -1,
            })

    def _cleanupDispatchDialog(self):
        if self.dispatchDialog:
            self.dispatchDialog.destroy()
            self.dispatchDialog = None
