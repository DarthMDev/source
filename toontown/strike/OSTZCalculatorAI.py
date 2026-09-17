from direct.stdpy.threading2 import Thread
from direct.controls.ControlManager import CollisionHandlerRayStart

from queue import Empty, Queue

from toontown.toonbase import ToontownGlobals
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna import DNAParser

from pandac.PandaModules import NodePath, CollisionTraverser, CollisionRay, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, BitMask32


class OSTZCalculatorAI(Thread):
    INSTANCE = None

    def __init__(self):
        Thread.__init__(self, target=self.__process, name='ost-z-calculator')

        store = DNAStorage()
        storageFiles = ['phase_4/dna/storage.pdna', 'phase_4/dna/storage_TT.pdna', 'phase_4/dna/storage_OST.pdna']
        DNAParser.DNABulkLoader(store, storageFiles).loadDNAFiles()

        node = DNAParser.loadDNAFile(store, 'phase_4/dna/operation_save_toontown.pdna')
        self.parent = NodePath('ost-z-calculator')
        self.geom = self.parent.attachNewNode(node)

        self.np = NodePath('ost-z-calculator-np')
        self.np.reparentTo(self.parent)

        self.cTrav = CollisionTraverser('ost-z-calculator-ctrav')
        cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)

        cn = CollisionNode('ost-z-calculator-ray')
        cn.addSolid(cRay)
        cn.setFromCollideMask(ToontownGlobals.FloorBitmask)
        cn.setIntoCollideMask(BitMask32.allOff())
        cnp = self.np.attachNewNode(cn)

        self.cHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(cnp, self.cHandler)

        self.requests = Queue()
        self.results = Queue()

    def calculateZ(self, x, y, callback):
        self.requests.put((x, y, callback))

    def __process(self):
        while True:
            x, y, callback = self.requests.get()
            self.np.setPos(x, y, 0)

            self.cHandler.clearEntries()
            self.cTrav.traverse(self.parent)

            entries = []

            for i in range(self.cHandler.getNumEntries()):
                entry = self.cHandler.getEntry(i)
                entries.append(entry)

            entries.sort(key=lambda entry: entry.getSurfacePoint(self.parent).getZ(),
                         reverse=True)
            if len(entries) > 0:
                z = entries[0].getSurfacePoint(self.parent).getZ()
            else:
                z = 0

            self.results.put((callback, z))

    def deliverResults(self, task):
        while True:
            try:
                callback, z = self.results.get_nowait()
            except Empty:
                break
            callback(z)
        return task.cont

    @staticmethod
    def createInstance():
        OSTZCalculatorAI.INSTANCE = OSTZCalculatorAI()
        taskMgr.add(OSTZCalculatorAI.INSTANCE.deliverResults,
                    'ost-z-calculator-results')
        OSTZCalculatorAI.INSTANCE.start()
