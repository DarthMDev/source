import time
from collections import OrderedDict

from direct.directnotify import DirectNotifyGlobal
from direct.task import Task

from toontown.web.ChatLog import websiteUserId

AV_SET_SIZE = 6


class ToonRoster:
    """
    Keeps the website's copy of each account's Toons current.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('ToonRoster')

    FLUSH_SECONDS = 1.0
    SETTLE_SECONDS = 1.0
    MAX_BATCH = 50
    MAX_PENDING = 5000

    def __init__(self, air, socket):
        self.air = air
        self.socket = socket
        self.pending = OrderedDict()

        taskMgr.doMethodLater(
            self.FLUSH_SECONDS, self.flushTask, 'toon-roster-flush')

    def sync(self, accountId):
        if self.socket is None or not accountId:
            return

        accountId = int(accountId)

        self.pending.pop(accountId, None)
        self.pending[accountId] = time.time()

        if len(self.pending) > self.MAX_PENDING:
            self.pending.popitem(last=False)

    def syncToon(self, avId):
        if self.socket is None:
            return

        try:
            toon = self.find(avId)
        except Exception as error:
            self.notify.warning('Could not read %s: %s' % (avId, error))
            return

        if toon:
            self.sync(toon['fields'].get('setDISLid', {}).get('_0'))

    def flushTask(self, task):
        self.flush()
        return Task.again

    def flush(self):
        if not self.pending or self.socket is None:
            return

        app = getattr(self.socket, 'app', None)
        connection = getattr(app, 'sock', None)
        if not connection or not connection.connected:
            return

        settled = time.time() - self.SETTLE_SECONDS
        accounts = []

        while self.pending and len(accounts) < self.MAX_BATCH:
            accountId, askedAt = next(iter(self.pending.items()))
            if askedAt > settled:
                break

            del self.pending[accountId]

            try:
                roster = self.roster(accountId)
            except Exception as error:
                # A Toon that could not be read would look deleted, so the
                # whole account waits for another try
                self.notify.warning(
                    'Could not read account %d: %s' % (accountId, error))
                self.sync(accountId)
                continue

            if roster is not None:
                accounts.append(roster)

        if accounts:
            self.socket.send({'type': 'toons', 'accounts': accounts})

    def roster(self, accountId):
        account = self.find(accountId)
        if not account or account.get('dclass') != 'Account':
            return None

        # Legacy and retired accounts belong to nobody on the website
        userId = websiteUserId(account)
        if userId is None:
            return None

        toons = []
        avSet = account['fields'].get('ACCOUNT_AV_SET') or []

        for slot, avId in enumerate(avSet[:AV_SET_SIZE]):
            if not int(avId):
                continue

            toon = self.find(avId)
            name = displayName(toon['fields']) if toon else None
            if name:
                toons.append({'id': str(int(avId)), 'name': name, 'slot': slot})

        return {'userId': userId, 'toons': toons}

    def find(self, doId):
        return self.air.dbAstronCursor.objects.find_one({'_id': int(doId)})


def displayName(fields):
    name = fields.get('setName', {}).get('_0')

    if fields.get('WishNameState', {}).get('_0') == 'APPROVED':
        name = fields.get('WishName', {}).get('_0') or name

    return name
