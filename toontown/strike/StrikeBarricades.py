from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject

from panda3d.core import CollisionBox, CollisionNode, CollisionSphere, Point3, TextNode

from toontown.toonbase import ToontownGlobals



BARRICADES = (
    {
        'name': 'HQ Approach',
        'cost': 750,
        'nodes': ('**/barricade_1', '**/barricade_3',
                  '**/prop_ttc_statue_DNARoot', '**/prop_blockade_DNARoot'),
        'description': 'CLEAR HQ BLOCKADE',
        'collisionNodes': ('**/prop_ttc_statue_DNARoot',
                           '**/prop_blockade_DNARoot'),
        'trigger': (59.0, 132.0, 6.0, 29.0),
    },
    {
        'name': 'Fortress Gate',
        'cost': 1500,
        'nodes': ('**/cog_blocker', '**/cog_blocker_collision'),
        'activationNode': '**/prop_gov_wall_entrance_DNARoot',
        'trigger': (-8.55, -1.55, 4.0, 7.0),
        'description': 'OPEN FORTRESS GATE',
        'blocker': (-8.55, -1.55, 0.0, 0.0, 2.0, 10.0, 14.0),
    },
)


class StrikeBarricades(DirectObject):
    def __init__(self, strike):
        DirectObject.__init__(self)
        self.strike = strike
        self.mask = 0
        self.nearbyIndex = None
        self.triggers = []
        self.blockers = []
        self.prompt = None
        self.promptText = None

    def initialize(self):
        for index, barricade in enumerate(BARRICADES):
            self._createTrigger(index, barricade)
            self._createBlocker(index, barricade)
        self._createPrompt()
        self.applyMask()

    def _createBlocker(self, index, barricade):
        blocker = barricade.get('blocker')
        collisionNodes = barricade.get('collisionNodes', ())
        if blocker is None and not collisionNodes:
            self.blockers.append(None)
            return
        node = CollisionNode('strike-barricade-blocker-%s' % index)
        nodePath = self.strike.geom.attachNewNode(node)
        if collisionNodes:
            padding = Point3(0.5, 0.5, 0.2)
            for nodeName in collisionNodes:
                target = self.strike.geom.find(nodeName)
                if target.isEmpty():
                    continue
                bounds = target.getTightBounds(self.strike.geom)
                if bounds:
                    node.addSolid(CollisionBox(bounds[0] - padding,
                                               bounds[1] + padding))
        else:
            x, y, z, heading, width, depth, height = blocker
            node.addSolid(CollisionBox(Point3(-width / 2, -depth / 2, 0),
                                       Point3(width / 2, depth / 2, height)))
            nodePath.setPosHpr(x, y, z, heading, 0, 0)
        node.setCollideMask(ToontownGlobals.WallBitmask)
        self.blockers.append(nodePath)

    def _createTrigger(self, index, barricade):
        x, y, z, radius = barricade['trigger']
        name = 'strike-barricade-%s' % index
        node = CollisionNode(name)
        sphere = CollisionSphere(x, y, z, radius)
        sphere.setTangible(0)
        node.addSolid(sphere)
        node.setCollideMask(ToontownGlobals.WallBitmask)
        nodePath = self.strike.geom.attachNewNode(node)
        self.triggers.append(nodePath)
        self.accept('enter' + name, self._enterBarricade, [index])
        self.accept('exit' + name, self._exitBarricade, [index])

    def _createPrompt(self):
        self.prompt = DirectFrame(parent=aspect2d, relief=None, pos=(0, 0, -0.72))
        self.promptText = OnscreenText(parent=self.prompt, text='', scale=0.042,
                                       align=TextNode.ACenter, font=ToontownGlobals.getToonFont(),
                                       fg=(1, 0.9, 0.25, 1), shadow=(0, 0, 0, 1),
                                       shadowOffset=(0.035, 0.035))
        self.prompt.hide()

    def _enterBarricade(self, index, entry):
        if not self._isUnlocked(index):
            self.nearbyIndex = index
            self._updatePrompt()

    def _exitBarricade(self, index, entry):
        if self.nearbyIndex == index:
            self.nearbyIndex = None
            self.prompt.hide()

    def _updatePrompt(self):
        if self.nearbyIndex is None:
            return
        barricade = BARRICADES[self.nearbyIndex]
        self.promptText.setText('%s  -  %s POINTS\n[ ACTION KEY ]' %
                                (barricade['description'], barricade['cost']))
        self.prompt.show()

    def _isUnlocked(self, index):
        return bool(self.mask & (1 << index))

    def tryPurchase(self):
        if self.nearbyIndex is None or self._isUnlocked(self.nearbyIndex):
            return False
        self.strike.sendUpdate('requestUnlockBarricade', [self.nearbyIndex])
        return True

    def setMask(self, mask):
        openedMask = mask & ~self.mask
        self.mask = mask
        self.applyMask()
        if openedMask:
            sound = ('phase_4/audio/corpstrike/cs_clear_debris.ogg'
                     if openedMask & 1 else
                     'phase_4/audio/corpstrike/cs_purchase.ogg')
            base.playSfx(loader.loadSfx(sound), volume=0.6)

    def applyMask(self):
        if not self.strike.geom:
            return
        for index, barricade in enumerate(BARRICADES):
            if not self._isUnlocked(index):
                continue
            for nodeName in barricade['nodes']:
                for node in self.strike.geom.findAllMatches(nodeName):
                    node.removeNode()
            if index < len(self.triggers):
                self.triggers[index].removeNode()
            if index < len(self.blockers) and self.blockers[index]:
                self.blockers[index].removeNode()
            if self.nearbyIndex == index:
                self.nearbyIndex = None
                if self.prompt:
                    self.prompt.hide()

    def destroy(self):
        self.ignoreAll()
        for trigger in self.triggers:
            trigger.removeNode()
        self.triggers = []
        for blocker in self.blockers:
            if blocker:
                blocker.removeNode()
        self.blockers = []
        if self.prompt:
            self.prompt.destroy()
            self.prompt = None
        self.promptText = None
