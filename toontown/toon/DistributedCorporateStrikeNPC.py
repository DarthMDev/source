from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog


class DistributedCorporateStrikeNPC(DistributedNPCToonBase):
    DISPATCH_MESSAGE = (
        'The Resistance needs your help in ruined Toontown Central! '
        'You can meet your friends at the Strike elevator once you arrive.')

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.dispatchDialog = None

    def disable(self):
        self._cleanupDispatchDialog()
        DistributedNPCToonBase.disable(self)

    def handleCollisionSphereEnter(self, collEntry):
        if self.dispatchDialog:
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
            })

    def _cleanupDispatchDialog(self):
        if self.dispatchDialog:
            self.dispatchDialog.destroy()
            self.dispatchDialog = None
