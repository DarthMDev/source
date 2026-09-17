from panda3d.core import NodePath, TextNode, Vec4

from direct.interval.IntervalGlobal import *
import random


class RoundCounter(NodePath):
    FONT = 'phase_3/models/fonts/vtRemingtonPortable.ttf'
    ROUND_START_SFX = (
        'phase_4/audio/corpstrike/cs_ost_round_start_1.ogg',
        'phase_4/audio/corpstrike/cs_ost_round_start_2.ogg',
        'phase_4/audio/corpstrike/cs_ost_round_start_3.ogg',
    )

    def __init__(self):
        NodePath.__init__(self, 'round-counter')

        self.round = None
        self.track = None

    def initialize(self):
        self.reparentTo(base.a2dBottomRight)
        self.setPos(-0.25, 0, 0.06)

    def generateRoundText(self, round):
        tn = TextNode('round-text')
        tn.setText(str(round))
        tn.setFont(loader.loadFont(self.FONT))
        tn.setTextColor(0.15, 0.15, 0.15, 1.0)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0.3, 0.3, 0.3, 1)
        return tn

    def removeRoundText(self):
        self.find('**/*round-text').removeNode()

    def attachRoundText(self, text):
        node = self.attachNewNode(text)
        node.setName('round-text')
        node.setScale(0.3)

    def transitionRound(self, round):
        if self.track:
            self.track.pause()
        newText = self.generateRoundText(round)

        if self.round is not None:
            roundEnd = Sequence(
                Parallel(
                    Sequence(
                        Func(self.setTransparency, 1),
                        LerpColorScaleInterval(self, 3, Vec4(1, 1, 1, 0), startColorScale=Vec4(1, 1, 1, 1)),
                        Func(self.clearColorScale),
                        Func(self.clearTransparency),
                        Func(self.hide)
                    ),
                ),
                Func(self.removeRoundText),
                Wait(5)
            )
        else:
            roundEnd = Sequence()

        roundStart = Parallel(
            Sequence(
                Func(self.attachRoundText, newText),
                Sequence(
                    Func(self.show),
                    Func(self.setTransparency, 1),
                    LerpColorScaleInterval(self, 4, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0)),
                    Func(self.clearColorScale),
                    Func(self.clearTransparency)
                 ),
            ),
            Func(base.playSfx, loader.loadSfx(random.choice(self.ROUND_START_SFX)), volume=0.35),
        )

        self.track = Sequence(
            roundEnd,
            roundStart,
        )
        self.track.start()

        self.round = round

    def destroy(self):
        if self.track:
            self.track.pause()
            self.track = None
        self.removeNode()
