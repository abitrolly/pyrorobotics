# class which provides visualization capabilities for conx
from pyro.brain.conx import *
import Tkinter
from TwoDimPlot import TwoDimPlot
import NetStruct
import Hinton
import ActivationsDiag
import tkMessageBox
import tkSimpleDialog
import ArchDiag

# general utility function for generating connection names from vertex names

class VisConxBase:
    def __init__(self, parent=None):
        #stuff
        self.interactive = 0
        
        #references to plots
        self.TSSPlot = None
        self.RMSPlot = None
        self.pCorrectPlot = None
        self.hintonDiags = {}
        self.archDiag = None
        self.activDiag = None
        
        #parsed network
        self.netStruct = NetStruct.NetStruct(self)

        #data variables
        self.TSSData = []
        self.RMSData = []
        self.pCorrectData = []

        #setup up GUI for selecting features
        if parent:
            self.root = Tkinter.Toplevel(parent)
        else:
            self.root = Tkinter.Tk()
        self.root.title("VisConx")

        #setup options for basic data plots
        Tkinter.Label(self.root, text="Plot:").grid(col=0, row=0, sticky= Tkinter.W)
        self.TSSCheck = Tkinter.Checkbutton(self.root, text="Show TSS Plot", command = self.handleTSSBox)
        self.TSSCheck.grid(col=1,row=0, sticky=Tkinter.W)
        self.RMSCheck = Tkinter.Checkbutton(self.root, text="Show RMS Plot", command = self.handleRMSBox)
        self.RMSCheck.grid(col=1,row=1, sticky=Tkinter.W)
        self.pCorrectCheck = Tkinter.Checkbutton(self.root, text="Show % Correct  Plot", command = self.handlePCorrectBox)
        self.pCorrectCheck.grid(col=1,row=2, sticky=Tkinter.W)

        #options for displaying hinton diagrams
        Tkinter.Label(self.root, text="Connections:").grid(col=0, row=3, sticky=Tkinter.NW)
        self.hintonListBox = Tkinter.Listbox(self.root, selectmode = Tkinter.SINGLE, height=4, width = 40)
        self.hintonListBox.grid(col=1, row=3, sticky=Tkinter.W)
        Tkinter.Button(self.root,text="Draw Hinton Diagram", command=self.createHintonDiag).grid(col=1,row=4, sticky=Tkinter.N)
        self.updateHintonListBox()

        #options for displaying the network topology
        Tkinter.Label(self.root, text="Network Architecture:").grid(col=0,row=5, sticky=Tkinter.W)
        self.archButton = Tkinter.Checkbutton(self.root, text="Draw network architecture", command=self.handleNetworkArchBox)
        self.archButton.grid(col=1,row=5, sticky=Tkinter.W)

        #options for displaying node activations
        Tkinter.Label(self.root, text="Node Activations:").grid(col=0,row=6,sticky=Tkinter.W)
        self.activButton = Tkinter.Checkbutton(self.root, text="Examine Node Activations", command=self.createActivDiag)
        self.activButton.grid(col=1,row=6,sticky=Tkinter.W)

        self.root.update_idletasks()
        
    #overloaded methods from Network/SRN
    def train(self):
        self.activButton.config(state=Tkinter.DISABLED)
        tssErr = 1.0; self.epoch = 1; totalCorrect = 0; totalCount = 1;
        self.resetCount = 1
        while totalCount != 0 and \
              totalCorrect * 1.0 / totalCount < self.stopPercent:
            (tssErr, totalCorrect, totalCount) = self.sweep()
            if self.epoch % self.reportRate == 0:
                self.root.update()
                #update data plots
                self.TSSData +=  [(self.epoch, tssErr)]
                self.updatePlot(self.TSSPlot, self.TSSData[-1])
                self.RMSData += [(self.epoch, self.RMSError())]
                self.updatePlot(self.RMSPlot, self.RMSData[-1])
                self.pCorrectData += [(self.epoch, totalCorrect * 1.0 / totalCount)]
                self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])

                #update Hinton diagram
                self.updateHintonWeights()
            if self.resetEpoch == self.epoch:
                if self.resetCount == self.resetLimit:
                    tkMessageBox.showinfo(title="Reset limit reached!", message="Reset limit reached. Ending without reaching goal.")
                    break
                self.resetCount += 1
                tkMessageBox.showinfo(title="RESET!", message="RESET! resetEpoch reached; starting over...")
                self.initialize()
                tssErr = 1.0; self.epoch = 1; totalCorrect = 0
                continue
            sys.stdout.flush()
            self.epoch += 1
        if totalCount > 0:
            self.TSSData +=  [(self.epoch, tssErr)]
            self.updatePlot(self.TSSPlot, self.TSSData[-1])
            self.RMSData += [(self.epoch, self.RMSError())]
            self.updatePlot(self.RMSPlot, self.RMSData[-1])
            self.pCorrectData += [(self.epoch, totalCorrect * 1.0 / totalCount)]
            self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])
        else:
            tkMessageBox.showinfo(title="Done", message="Final: nothing done")
        self.activButton.config(state=Tkinter.NORMAL)

    def propagate(self):
        #hack to allow intervention in sweep for purposes of extracting data
        self.__class__.__bases__[1].propagate(self)
        if self.activDiag:
            self.activDiag.extractActivs() 
        
    def add(self, newLayer, verbosity=0):
        Network.add(self,newLayer, verbosity=verbosity)
        self.updateAllDiags()

    def connect(self, fromLayer, toLayer):
        Network.connect(self, fromLayer, toLayer)
        self.updateAllDiags()
        
    def changeLayerSize(self, fromSize, toSize):
        Network.changeLayerSize(self, fromSize, toSize)
        self.updateAllDiags()
        
    def updateAllDiags(self):
        self.netStruct = NetStruct.NetStruct(self)
        self.updateHintonListBox()
        self.updateArchDiag()
        self.updateActivDiag()

    def setInteractive(self, val):
        pass 

    #handlers for error plotting code
    def updatePlot(self, plot, newTuple):
        if plot:
            plot.addPoint(newTuple)

    def handleTSSBox(self):
        if self.TSSPlot:
            self.TSSPlot.destroy()
            self.TSSPlot = None
            self.TSSCheck.deselect()
        else:
            self.TSSPlot = TwoDimPlot(self.root, plotName="TSS Plot",  xTitle="Epoch", yTitle="TSS Error", closeCallback=self.handleTSSBox, xMax=self.epoch)
            self.TSSPlot.addPoints(self.TSSData)
            self.TSSPlot.protocol("WM_DELETE_WINDOW", self.handleTSSBox)
            self.TSSCheck.select()

    def handleRMSBox(self):
        if self.RMSPlot:
            self.RMSPlot.destroy()
            self.RMSPlot = None
            self.RMSCheck.deselect()
        else:
            self.RMSPlot = TwoDimPlot(self.root, plotName="RMS Plot", xTitle="Epoch", yTitle="RMS Error", closeCallback=self.handleRMSBox, xMax=self.epoch)
            self.RMSPlot.addPoints(self.RMSData)
            self.RMSPlot.protocol("WM_DELETE_WINDOW", self.handleRMSBox)
            self.RMSCheck.select()

    def handlePCorrectBox(self):
        if self.pCorrectPlot:
            self.pCorrectPlot.destroy()
            self.pCorrectPlot = None
            self.pCorrectCheck.deselect()
        else:
            self.pCorrectPlot = TwoDimPlot(self.root, plotName="Percent Correct", xTitle="Epoch", yTitle="% Correct", \
                                           closeCallback=self.handlePCorrectBox, xMax=self.epoch)
            self.pCorrectPlot.addPoints(self.pCorrectData)
            self.pCorrectPlot.protocol("WM_DELETE_WINDOW", self.handlePCorrectBox)
            self.pCorrectCheck.select()

    #handlers for Hinton diagram code
    def updateHintonListBox(self):
        self.hintonListBox.delete(0,last=self.hintonListBox.size())
        self.connectionDict = {}
        
        for edge in self.netStruct.edgeList:
            newEntry = NetStruct.genName(edge)
            self.hintonListBox.insert(0, newEntry)
            self.connectionDict[newEntry] = edge

    def updateHintonWeights(self):
        for diag in self.hintonDiags.values():
            if diag:
                diag.updateDiag()

    class ConnectionHinton(Hinton.MatrixHinton):
        def __init__(self, parent, edge):
            self.edge = edge
            Hinton.MatrixHinton.__init__(self, parent, "Connection from %s to %s" % (edge.fromVer.name, edge.toVer.name), \
                                     edge.connection.weight, fromAxisLabel="From\n%s" % (edge.fromVer.name), \
                                         toAxisLabel="To\n%s" % (edge.toVer.name))

        def updateDiag(self):
            self.updateWeights(self.edge.connection.weight)

    def createHintonDiag(self):
        currentIndex = self.hintonListBox.curselection()
    
        if len(currentIndex) > 0:
            connectName = self.hintonListBox.get(currentIndex[0])

            if not self.hintonDiags.get(connectName,0):
                self.hintonDiags[connectName] = self.ConnectionHinton(self.root, self.connectionDict[connectName])
                self.hintonDiags[connectName].protocol("WM_DELETE_WINDOW", lambda name=connectName: self.destroyHintonDiag(name))

    def destroyHintonDiag(self, name):
        self.hintonDiags[name].destroy()
        self.hintonDiags[name] = None

    # handlers for network architecture diagram
    def handleNetworkArchBox(self):
        if not self.archDiag:
            self.archDiag = ArchDiag.ArchDiag(self.root,self.netStruct)
            self.archDiag.protocol("WM_DELETE_WINDOW", self.handleNetworkArchBox)
        else:
            self.archDiag.destroy()
            self.archDiag = None
            self.archButton.deselect()
            
    def updateArchDiag(self):
        if self.archDiag:
            archDiag.destroy()
            archDiag = ArchDiag.ArchDiag(self.root, self.netStruct)
            
    #handlers for activations diagram
    def createActivDiag(self):
        if not self.activDiag:
            try:
                self.activDiag = ActivationsDiag.ActivDiag(self.root,self.netStruct)
            except:
                tkMessageBox.showerror("Activtions Display Error", "You must set inputs and outputs using setInputs and setOutputs before using the activation display")
                self.activDiag.destroy()
                self.activDiag = None
                self.activButton.deselect()
            else:
                self.activDiag.protocol("WM_DELETE_WINDOW", self.createActivDiag)
        else:
            self.activDiag.destroy()
            self.activDiag = None
            self.activButton.deselect()
                              
    def updateActivDiag(self):
        if self.activDiag:
            self.activDiag.destroy()
            self.activDiag = ActivationsDiag.ActivDiag(self.root,self.netStruct)           

    def destroy(self):
        self.root.destroy()
        
class VisNetwork(VisConxBase, Network): 
    def __init__(self, parent=None):
        Network.__init__(self)
        VisConxBase.__init__(self, parent=parent)
        
class VisSRN(VisConxBase, SRN):
    def __init__(self, parent=None):
        SRN.__init__(self)
        VisConxBase.__init__(self, parent=parent)
        
if __name__ == "__main__":
    def testXORBatch():
        n = VisNetwork(root)
        n.addThreeLayers(2, 2, 1)
        n.setInputs([[0.0, 0.0],
                     [0.0, 1.0],
                     [1.0, 0.0],
                     [1.0, 1.0]])
        n.setTargets([[0.0],
                      [1.0],
                      [1.0],
                      [0.0]])
        n.setReportRate(100)
        n.setBatch(1)
        n.reset()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()
        
    def testXORNonBatch():
        n = VisNetwork(root)
        n.addThreeLayers(2, 2, 1)
        n.setInputs([[0.0, 0.0],
                     [0.0, 1.0],
                     [1.0, 0.0],
                     [1.0, 1.0]])
        n.setTargets([[0.0],
                      [1.0],
                      [1.0],
                      [0.0]])
        n.setReportRate(100)
        n.setBatch(0)
        n.initialize()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()
        
    def testAND():
        n = VisNetwork(root)
        #n.setSeed(114366.64)
        n.add(Layer('input',2)) 
        n.add(Layer('output',1)) 
        n.connect('input','output') 
        n.setInputs([[0.0,0.0],[0.0,1.0],[1.0,0.0],[1.0,1.0]]) 
        n.setTargets([[0.0],[0.0],[0.0],[1.0]]) 
        n.setEpsilon(0.5) 
        n.setTolerance(0.2) 
        n.setReportRate(5) 
        n.train() 
   
    def testSRN():
        n = VisSRN(root)
        #n.setSeed(114366.64)
        n.addSRNLayers(3,2,3)
        n.predict('input','output')
        seq1 = [1,0,0, 0,1,0, 0,0,1]
        seq2 = [1,0,0, 0,0,1, 0,1,0]
        n.setInputs([seq1, seq2])
        n.setLearnDuringSequence(1)
        n.setReportRate(75)
        n.setEpsilon(0.1)
        n.setMomentum(0)
        n.setBatch(1)
        n.setTolerance(0.25)
        n.setStopPercent(0.7)
        n.setResetEpoch(2000)
        n.setResetLimit(0)
        #n.setInteractive(1)
        #n.verbosity = 3
        n.train()

    def testAutoAssoc():
        n = VisNetwork(root)
        #n.setSeed(114366.64)
        n.addThreeLayers(3,2,3)
        n.setInputs([[1,0,0],[0,1,0],[0,0,1],[1,1,0],[1,0,1],[0,1,1],[1,1,1]])
        n.associate('input','output')
        n.setReportRate(25)
        n.setEpsilon(0.1)
        n.setMomentum(0.9)
        n.setBatch(1)
        n.setTolerance(0.25)
        n.setStopPercent(0.9)
        n.setResetEpoch(1000)
        n.setResetLimit(2)
        n.train()

    def testRAAM():
        # create network:
        raam = VisSRN(root)
        #raam.setSeed(114366.64)
        raam.setPatterns({"john"  : [0, 0, 0, 1],
                          "likes" : [0, 0, 1, 0],
                          "mary"  : [0, 1, 0, 0],
                          "is" : [1, 0, 0, 0],
                          })
        size = len(raam.getPattern("john"))
        raam.addSRNLayers(size, size * 2, size)
        raam.add( Layer("outcontext", size * 2) )
        raam.connect("hidden", "outcontext")
        raam.associate('input', 'output')
        raam.associate('context', 'outcontext')
        raam.setInputs([ [ "john", "likes", "mary" ],
                         [ "mary", "likes", "john" ],
                         [ "john", "is", "john" ],
                         [ "mary", "is", "mary" ],
                         ])
        # network learning parameters:
        raam.setLearnDuringSequence(1)
        raam.setReportRate(10)
        raam.setEpsilon(0.1)
        raam.setMomentum(0.0)
        raam.setBatch(0)
        # ending criteria:
        raam.setTolerance(0.4)
        raam.setStopPercent(1.0)
        raam.setResetEpoch(5000)
        raam.setResetLimit(0)
        # train:
        raam.train()
        raam.setLearning(0)

    def testSRNPredictAuto():
        n = VisSRN(root)
        #n.setSeed(114366.64)
        n.addSRNLayers(3,3,3)
        n.add(Layer('assocInput',3))
        n.connect('hidden', 'assocInput')
        n.associate('input', 'assocInput')
        n.predict('input', 'output')
        n.setInputs([[1,0,0, 0,1,0, 0,0,1, 0,0,1, 0,1,0, 1,0,0]])
        n.setLearnDuringSequence(1)
        n.setReportRate(25)
        n.setEpsilon(0.1)
        n.setMomentum(0.3)
        n.setBatch(1)
        n.setTolerance(0.1)
        n.setStopPercent(0.7)
        n.setResetEpoch(2000)
        n.setResetLimit(0)
        n.setOrderedInputs(1)
        n.train()
        n.setLearning(0)
        n.setInteractive(1)

    def testChangeLayerSize():
        n = VisNetwork(root)
        n.addThreeLayers(3,3,3)
        n.archButton.invoke()
        size = tkSimpleDialog.askinteger("Change hidden layer size", "Enter new hidden layer size", minvalue=0)
        n.archButton.invoke()
        try:
            # exception thrown from changeSize in Connection class
            n.changeLayerSize('hidden', size)
        except LayerError, err:
            print err
        n.archButton.invoke()

    def dispatchToTest():
        index = int(testList.curselection()[0])
        callList[index]()
        
    root = Tkinter.Tk()
    testList = Tkinter.Listbox(root, selectmode=Tkinter.SINGLE, width=50)

    listButton = Tkinter.Button(root, text="Run test", command=dispatchToTest)
    nameList = ["Test XOR in batch mode",
                "Test XOR in non-batch mode",
                "Test AND",
                "Test SRN",
                "Test auto association",
                "Test RAAM",
                "Test SRN with prediction and auto association",
                "Test changing a layer's size"]
    callList = [testXORBatch, testXORNonBatch, testAND, testSRN, testAutoAssoc, testRAAM,testSRNPredictAuto, \
                testChangeLayerSize]
    
    for name in nameList:
        testList.insert(Tkinter.END, name)
        testList.pack()
        listButton.pack()
                
