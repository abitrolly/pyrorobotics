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
import time

class NNSettingsDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, network):
        self.entryList = [("Learning rate (epsilon)",network.setEpsilon, network.epsilon, Tkinter.StringVar(parent),
                           lambda val: 0.0 <= val <= 1.0, lambda var: float(var.get()), "Value must on the interval [0,1]."),
                          ("Momentum",network.setMomentum, network.momentum, Tkinter.StringVar(parent),
                           lambda val: 0.0 <= val <= 1.0, lambda var: float(var.get()), "Value must on the interval [0,1]."),
                          ("Correctness tolerance",network.setTolerance, network.tolerance, Tkinter.StringVar(parent),
                           lambda val: 0.0 <= val <= 1.0, lambda var: float(var.get()), "Value must on the interval [0,1]."),
                          ("Reset epoch",network.setResetEpoch, network.resetEpoch, Tkinter.StringVar(parent),
                           lambda val: val > 0, lambda var: int(var.get()), "Value must be an integer greater than 0."),
                          ("Reset limit",network.setResetLimit, network.resetLimit, Tkinter.StringVar(parent),
                           lambda val: val >= 0, lambda var: int(var.get()), "Value must be an integer greater than or equal to 0.")]
        self.checkList = [("Learn",network.setLearning, network.learning, Tkinter.IntVar(parent)),
                          ("Batch mode",network.setBatch, network.batch, Tkinter.IntVar(parent)),
                          ("Ordered inputs",network.setOrderedInputs, network.orderedInputs, Tkinter.IntVar(parent))]
        
        #set the widget variables
        for paramTuple in self.entryList+self.checkList:
            paramTuple[3].set(paramTuple[2])

        tkSimpleDialog.Dialog.__init__(self, parent, title="Change Network Settings")
        
    def body(self, parent):
        i=0
        for paramTuple in self.entryList:
            Tkinter.Label(parent,text=paramTuple[0]).grid(row=i,col=0,sticky=Tkinter.W)
            Tkinter.Entry(parent, textvariable=paramTuple[3]).grid(row=i, col=1, sticky=Tkinter.W)
            i += 1
            
        i=0
        for paramTuple in self.checkList:
            tempLabel = Tkinter.Label(parent, text=paramTuple[0]).grid(row=i,col=2,sticky=Tkinter.W)
            Tkinter.Checkbutton(parent, variable=paramTuple[3]).grid(row=i, col=3, sticky=Tkinter.W)
            i += 1

    def validate(self):
        for paramTuple in self.entryList:
            try:
                var = paramTuple[3]
                conversion = paramTuple[5]
                boundsCheck = paramTuple[4]
                if not boundsCheck(conversion(var)):
                    tkMessageBox.showerror(title=key, message=paramTuple[6])
                    return 0
            except ValueError:
                tkMessageBox.showerror(title=key, message=paramTuple[6])
                return 0

        return 1

    def apply(self):
        for paramTuple in self.entryList:
            var = paramTuple[3]
            conversion = paramTuple[5]
            setFunction = paramTuple[1]
            setFunction(conversion(var))
            
        for paramTuple in self.checkList:
            var = paramTuple[3]
            setFunction = paramTuple[1]
            setFunction(var.get())
                              
class ConxGUIBase:
    def __init__(self):
        #interactive mode causes problems
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

        self.root = Tkinter.Tk()
        self.root.title("VisConx")
        self.root.resizable(0,0)

        self.visualFrame = Tkinter.Frame(self.root)
        Tkinter.Label(self.visualFrame, text="Visualization Tools:", font=("Arial", 14, "bold")).grid(row=0, col=0, columnspan=2, sticky=Tkinter.W)
        
        #setup options for basic data plots
        Tkinter.Label(self.visualFrame, text="Plot:").grid(col=0, row=1, sticky= Tkinter.W)
        self.TSSCheck = Tkinter.Checkbutton(self.visualFrame, text="Show TSS Plot", command = self.handleTSSBox)
        self.TSSCheck.grid(col=1,row=1, sticky=Tkinter.W)
        self.RMSCheck = Tkinter.Checkbutton(self.visualFrame, text="Show RMS Plot", command = self.handleRMSBox)
        self.RMSCheck.grid(col=1,row=2, sticky=Tkinter.W)
        self.pCorrectCheck = Tkinter.Checkbutton(self.visualFrame, text="Show % Correct  Plot", command = self.handlePCorrectBox)
        self.pCorrectCheck.grid(col=1,row=3, sticky=Tkinter.W)

        #options for displaying hinton diagrams
        Tkinter.Label(self.visualFrame, text="Connections:").grid(col=0, row=4, sticky=Tkinter.NW)
        self.hintonListBox = Tkinter.Listbox(self.visualFrame, selectmode = Tkinter.SINGLE, height=4, width = 40)
        self.hintonListBox.grid(col=1, row=4, sticky=Tkinter.W)
        Tkinter.Button(self.visualFrame,text="Draw Hinton Diagram", command=self.createHintonDiag).grid(col=1,row=5, sticky=Tkinter.N)
        self.refreshHintonListBox()

        #options for displaying the network topology
        Tkinter.Label(self.visualFrame, text="Network Architecture:").grid(col=0,row=6, sticky=Tkinter.W)
        self.archButton = Tkinter.Checkbutton(self.visualFrame, text="Draw network architecture", command=self.handleNetworkArchBox)
        self.archButton.grid(col=1,row=6, sticky=Tkinter.W)

        #options for displaying node activations
        Tkinter.Label(self.visualFrame, text="Node Activations:").grid(col=0,row=7,sticky=Tkinter.W)
        self.activButton = Tkinter.Checkbutton(self.visualFrame, text="Examine Node Activations", command=self.handleActivDiag)
        self.activButton.grid(col=1,row=7,sticky=Tkinter.W)

        #evaluation window
        self.inputFrame = Tkinter.Frame(self.root)

        inputLabelFrame = Tkinter.Frame(self.inputFrame)
        Tkinter.Label(inputLabelFrame, text="Conx Input:", font=("Arial", 14, "bold")).pack(side=Tkinter.LEFT)
        inputLabelFrame.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=Tkinter.YES)
        
        #output and scroll bar
        self.textFrame = Tkinter.Frame(self.inputFrame)
        self.textOutput = Tkinter.Text(self.textFrame, width = 40, height = 10,
                                   state=Tkinter.DISABLED, wrap=Tkinter.WORD)
        self.textOutput.pack(side=Tkinter.LEFT, expand=Tkinter.YES, fill=Tkinter.X)
        scrollbar = Tkinter.Scrollbar(self.textFrame, command=self.textOutput.yview)
        scrollbar.pack(side=Tkinter.LEFT,expand=Tkinter.NO,fill=Tkinter.Y)
        self.textOutput.configure(yscroll=scrollbar.set)
        self.textFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)

        #input box
        Tkinter.Label(self.inputFrame, text="Command:").pack(side=Tkinter.LEFT)
        self.commandEntry = Tkinter.Entry(self.inputFrame)
        self.commandEntry.bind("<Return>", self.handleCommand)
        self.commandEntry.pack(side=Tkinter.LEFT,expand=Tkinter.YES,fill="x")
              
        self.root.update_idletasks()
    
    #overloading methods from Network/SRN
    def add(self, newLayer, verbosity=0):
        Network.add(self, newLayer, verbosity=verbosity)
        self.updateStructureDiags()

    def connect(self, fromLayer, toLayer):
        Network.connect(self, fromLayer, toLayer)
        self.updateStructureDiags()

    def associate(self, fromLayer, toLayer):
        Network.associate(self, fromLayer, toLayer)
        self.updateStructureDiags()

    def changeLayerSize(self, fromSize, toSize):
        Network.changeLayerSize(self, fromSize, toSize)
        self.updateStructureDiags()
        
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
            self.TSSPlot = TwoDimPlot(self.root, plotName="TSS Plot",  xTitle="Epoch", yTitle="TSS Error", closeCallback=self.handleTSSBox)
            self.TSSPlot.addPoints(self.TSSData)
            self.TSSPlot.protocol("WM_DELETE_WINDOW", self.handleTSSBox)
            self.TSSCheck.select()

    def handleRMSBox(self):
        if self.RMSPlot:
            self.RMSPlot.destroy()
            self.RMSPlot = None
            self.RMSCheck.deselect()
        else:
            self.RMSPlot = TwoDimPlot(self.root, plotName="RMS Plot", xTitle="Epoch", yTitle="RMS Error", closeCallback=self.handleRMSBox)
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
                                           closeCallback=self.handlePCorrectBox)
            self.pCorrectPlot.addPoints(self.pCorrectData)
            self.pCorrectPlot.protocol("WM_DELETE_WINDOW", self.handlePCorrectBox)
            self.pCorrectCheck.select()

    #handlers for Hinton diagram code
    def refreshHintonListBox(self):
        self.hintonListBox.delete(0,last=self.hintonListBox.size())
        self.connectionDict = {}
        
        for edge in self.netStruct.conList:
            newEntry = "From: %s To: %s" % (edge.fromVer.name, edge.toVer.name)
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
            
    def refreshArchDiag(self):
        if self.archDiag:
            archDiag.destroy()
            archDiag = ArchDiag.ArchDiag(self.root, self.netStruct)
            
    def destroy(self):
        self.root.destroy()

    #handlers for command line
    def handleCommand(self, event):
        self.redirectToWindow()
        from string import strip
        command2 = strip(self.commandEntry.get())
        command1 = "_retval=" + command2
        self.commandEntry.delete(0, 'end')
        print ">>> " + command2
        try:
            exec command1
        except:
            try:
                exec command2
            except:
                print self.formatExceptionInfo()
        else:
            print _retval
        self.redirectToTerminal()

    def formatExceptionInfo(self, maxTBlevel=1):
        import sys, traceback
        cla, exc, trbk = sys.exc_info()
        if cla.__dict__.get("__name__") != None:
            excName = cla.__name__  # a real exception object
        else:
            excName = cla   # one our fake, string exceptions
            try:
                excArgs = exc.__dict__["args"]
            except KeyError:
                excArgs = ("<no args>",)
        excTb = traceback.format_tb(trbk, maxTBlevel)
        return "%s: %s %s" % (excName, excArgs[0], "in command line")

    def write(self, item):
        try:
            self.textOutput.config(state='normal')
            self.textOutput.insert('end', "%s" % (item))
            self.textOutput.config(state='disabled')
            self.textOutput.see('end')
        except:
            pass

    def redirectToWindow(self):
        # --- save old sys.stdout, sys.stderr
        self.sysstdout = sys.stdout
        sys.stdout = self # has a write() method
        self.sysstderror = sys.stderr
        sys.stderr = self # has a write() method
        
    def redirectToTerminal(self):
        # --- save old sys.stdout, sys.stderr
        sys.stdout = self.sysstdout
        sys.stderr = self.sysstderror

    #handlers for activation diagram 
    def handleActivDiag(self): #must be overloaded in derived class
        pass

    def refreshActivDiag(self):
        if self.activDiag:
            self.activDiag.reset()
    
    #routine to update diagrams if changes occur
    def updateStructureDiags(self):
        self.netStruct = NetStruct.NetStruct(self)
        self.refreshHintonListBox()
        self.refreshArchDiag()
        self.refreshActivDiag()

class SweepGUIBase(ConxGUIBase):
    def __init__(self):
        ConxGUIBase.__init__(self)
        self.pausedFlag = 0
        self.stopFlag = 0
        
        #start/pause/stop buttons       
        controlFrame = Tkinter.Frame(self.root)
        labelFrame = Tkinter.Frame(controlFrame)
        Tkinter.Label(labelFrame, text="Controls:", font=("Arial", 14, "bold")).pack(side=Tkinter.LEFT)
        labelFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        innerButtonFrame = Tkinter.Frame(controlFrame)
        self.trainButton = Tkinter.Button(innerButtonFrame, text="Start", command=self.handleTrainButton)
        self.trainButton.pack(side=Tkinter.LEFT)
        self.pauseButton = Tkinter.Button(innerButtonFrame, text="Pause", state=Tkinter.DISABLED, command=self.handlePauseButton)
        self.pauseButton.pack(side=Tkinter.LEFT)
        self.stopButton = Tkinter.Button(innerButtonFrame, text="Stop", state=Tkinter.DISABLED, command=self.handleStopButton)
        self.stopButton.pack(side=Tkinter.LEFT)
        self.settingsButton = Tkinter.Button(innerButtonFrame, text="Settings..", command=lambda: NNSettingsDialog(self.root, self.netStruct.network))
        self.settingsButton.pack(side=Tkinter.RIGHT)
        innerButtonFrame.pack(side=Tkinter.BOTTOM, expand=Tkinter.YES, fill=Tkinter.X)

        #assemble frames
        controlFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        Tkinter.Frame(self.root, height=2, bg="black").pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X) #spacer
        self.visualFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        Tkinter.Frame(self.root, height=2, bg="black").pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X) #spacer
        self.inputFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        
    #overloaded methods from Network/SRN
    def train(self):
        if self.activDiag:
            self.handleActivDiag()
        self.activButton.config(state=Tkinter.DISABLED)
        tssErr = 1.0; self.epoch = 1; totalCorrect = 0; totalCount = 1;
        self.resetCount = 1
        while totalCount != 0 and \
              totalCorrect * 1.0 / totalCount < self.stopPercent:
            (tssErr, totalCorrect, totalCount) = self.sweep()
            if self.pausedFlag:
                self.activButton.config(state=Tkinter.NORMAL)
                while self.pausedFlag and not self.stopFlag:
                    self.root.update()
                self.activButton.config(state=Tkinter.DISABLED)
                if self.activDiag:
                    self.handleActivDiag()
            if self.stopFlag:
                break
    
            self.root.update()
            #update data plots
            self.TSSData +=  [(self.epoch, tssErr)]
            self.updatePlot(self.TSSPlot, self.TSSData[-1])
            self.RMSData += [(self.epoch, self.RMSError())]
            self.updatePlot(self.RMSPlot, self.RMSData[-1])
            self.pCorrectData += [(self.epoch, float(totalCorrect)/totalCount)]
            self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])
            
            #update Hinton diagram
            self.updateHintonWeights()
            if self.resetEpoch == self.epoch:
                if self.resetCount == self.resetLimit:
                    self.write("Reset limit reached. Ending without reaching goal.")
                    break
                self.resetCount += 1
                self.write("RESET! resetEpoch reached; starting over...")
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
            self.write("Nothing done.")
        self.activButton.config(state=Tkinter.NORMAL)

    def propagate(self):
        #hack to allow intervention in sweep for purposes of extracting data
        self.__class__.__bases__[1].propagate(self)
        if self.activDiag:
            self.activDiag.extractActivs() 

    #handlers for activations diagram
    def handleActivDiag(self):
        if not self.activDiag:
            try:
                self.activDiag = ActivationsDiag.ActivSweepDiag(self.root,self.netStruct)
            except LayerError:
                self.write("Error! You must have called setInputs and setOutputs before using the activation display.")
                self.activDiag.destroy()
                self.activDiag = None
                self.activButton.deselect()
            else:
                self.activDiag.protocol("WM_DELETE_WINDOW", self.handleActivDiag)
        else:
            self.activDiag.destroy()
            self.activDiag = None
            self.activButton.deselect()

    #handlers for buttons
    def handleTrainButton(self):
            self.pausedFlag = 0
            self.stopFlag = 0
            self.pauseButton.config(state=Tkinter.NORMAL)
            self.stopButton.config(state=Tkinter.NORMAL)
            self.trainButton.config(state=Tkinter.DISABLED)
            
            #clear data collected during the last run
            self.initialize()
            self.TSSData = []
            if self.TSSPlot:
                self.TSSPlot.clearData()
            self.RMSData = []
            if self.RMSPlot:
                self.RMSPlot.clearData()
            self.pCorrectData = []
            if self.pCorrectPlot:
                self.pCorrectPlot.clearData()
            try:
                self.train()
            except AttributeError:
                self.write("Error!  Must call setInputs and setOutputs before training.")

            #set buttons and flags back after train concludes
            self.trainButton.config(state=Tkinter.NORMAL)
            self.pauseButton.config(state=Tkinter.DISABLED)
            self.pauseButton.config(text="Pause")
            self.stopButton.config(state=Tkinter.DISABLED)
            self.pausedFlag=0
            self.stopFlag=0

    def handlePauseButton(self):
        if not self.pausedFlag:
            self.pausedFlag = 1
            self.trainButton.config(state=Tkinter.DISABLED)
            self.stopButton.config(state=Tkinter.NORMAL)
            self.pauseButton.config(text="Resume")
        else:
            self.pausedFlag = 0
            self.pauseButton.config(text="Pause")            

    def handleStopButton(self):
        self.stopFlag = 1
        self.pausedFlag = 0
        self.trainButton.config(state=Tkinter.NORMAL)
        self.pauseButton.config(state=Tkinter.DISABLED)
        self.stopButton.config(state=Tkinter.DISABLED)


class VisNetwork(SweepGUIBase, Network): 
    def __init__(self):
        Network.__init__(self)
        SweepGUIBase.__init__(self)
        
class VisSRN(SweepGUIBase, SRN):
    def __init__(self):
        SRN.__init__(self)
        SweepGUIBase.__init__(self)

    def predict(self, fromLayer, toLayer):
        SRN.predict(self, fromLayer, toLayer)
        self.updateStructureDiags()

class RobotGUIBase(ConxGUIBase):
    def __init__(self):
        ConxGUIBase.__init__(self)
        buttonFrame = Tkinter.Frame(self.root)
        Tkinter.Label(buttonFrame, text="Controls:", font=("Arial", 14, "bold")).grid(row=0, col=0, sticky=Tkinter.W)
        Tkinter.Button(buttonFrame, text="Settings...", command=lambda: NNSettingsDialog(self.root, self.netStruct.network)).grid(row=1, col=0, sticky=Tkinter.W)
        self.visualFrame.grid(row=2, col=0, sticky=Tkinter.NSEW)
        Tkinter.Frame(self.root, height=2, bg="black").grid(row=3,col=0,sticky=Tkinter.NSEW)
        self.inputFrame.grid(row=4,col=0, sticky=Tkinter.NSEW)
        self.propNum = 0
        
    def handleActivDiag(self):
        if not self.activDiag:
            try:
                self.activDiag = ActivationsDiag.ActivDiag(self.root,self.netStruct)
            except LayerError:
                self.write("Error! You must have called setInputs and setOutputs before using the activation display.")
                self.activDiag.destroy()
                self.activDiag = None
                self.activButton.deselect()
            else:
                self.activDiag.protocol("WM_DELETE_WINDOW", self.handleActivDiag)
        else:
            self.activDiag.destroy()
            self.activDiag = None
            self.activButton.deselect()

    def propagate(self):
        self.updateGUI()
        self.__class__.__bases__[1].propagate(self)
        self.propNum += 1
        if self.activDiag:
            self.activDiag.updateActivs()
        self.updateHintonWeights()

    def backprop(self):
        (error, correct, total) = self.__class__.__bases__[1].backprop(self)
        
        self.TSSData +=  [(self.propNum, error)]
        self.updatePlot(self.TSSPlot, self.TSSData[-1])
        self.RMSData += [(self.propNum, self.RMSError())]
        self.updatePlot(self.RMSPlot, self.RMSData[-1])
        self.pCorrectData += [(self.propNum, float(correct)/total)]
        self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])

        return (error,correct, total)

    def updateGUI(self):
        self.root.update()
            
class VisRobotNetwork(RobotGUIBase, Network):
    def __init__(self):
        Network.__init__(self)
        RobotGUIBase.__init__(self)

class VisRobotSRN(RobotGUIBase, SRN):
    def __init__(self):
        SRN.__init__(self)
        RobotGUIBase.__init__(self)

    def predict(self, fromLayer, toLayer):
        SRN.predict(self, fromLayer, toLayer)
        self.updateStructureDiags()
    
if __name__ == "__main__":
    def testXORBatch():
        n = VisNetwork()
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
        
    def testXORNonBatch():
        n = VisNetwork()
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
        n = VisNetwork()
        #n.setSeed(114366.64)
        n.add(Layer('input',2)) 
        n.add(Layer('output',1)) 
        n.connect('input','output') 
        n.setInputs([[0.0,0.0],[0.0,1.0],[1.0,0.0],[1.0,1.0]]) 
        n.setTargets([[0.0],[0.0],[0.0],[1.0]]) 
        n.setEpsilon(0.5) 
        n.setTolerance(0.2) 
        n.setReportRate(5) 
   
    def testSRN():
        n = VisSRN()
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

    def testAutoAssoc():
        n = VisNetwork()
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

    def testRAAM():
        # create network:
        raam = VisSRN()
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

    def testSRNPredictAuto():
        n = VisSRN()
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

    def testChangeLayerSize():
        n = VisNetwork()
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

    def testFauxRobotAND():
        n = VisRobotNetwork()
        n.add(Layer('input', 2))
        n.add(Layer('output',1))
        n.connect('input','output')

        inputs = [[1,1],[0,0],[0,1],[1,0]]
        targets = [[1],[0],[0],[0]]
        for i in xrange(200):
            for j in xrange(3):
                n.getLayer('input').copyActivations(inputs[j])
                n.getLayer('output').copyTargets(targets[j])
                n.step()
                time.sleep(.3)       
            
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
                "Test changing a layer's size",
                "Test VisRobotNetwork with an AND network"]
    callList = [testXORBatch, testXORNonBatch, testAND, testSRN, testAutoAssoc, testRAAM,testSRNPredictAuto, \
                testChangeLayerSize, testFauxRobotAND]
    
    for name in nameList:
        testList.insert(Tkinter.END, name)
        testList.pack()
        listButton.pack()
                
    root.mainloop()
