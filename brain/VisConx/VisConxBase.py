import Tkinter
import tkMessageBox
import tkSimpleDialog
from pyro.brain.conx import *
import pyro.brain.VisConx.TwoDimPlot as TwoDimPlot
import pyro.brain.VisConx.NetStruct as NetStruct
import pyro.brain.VisConx.Hinton as Hinton
import pyro.brain.VisConx.ActivationsDiag as ActivationsDiag
import pyro.brain.VisConx.ArchDiag as ArchDiag

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
                              
class VisConxBase:
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
            self.TSSPlot = TwoDimPlot.TwoDimPlot(self.root, plotName="TSS Plot",  xTitle="Epoch", yTitle="TSS Error", closeCallback=self.handleTSSBox)
            self.TSSPlot.addPoints(self.TSSData)
            self.TSSPlot.protocol("WM_DELETE_WINDOW", self.handleTSSBox)
            self.TSSCheck.select()

    def handleRMSBox(self):
        if self.RMSPlot:
            self.RMSPlot.destroy()
            self.RMSPlot = None
            self.RMSCheck.deselect()
        else:
            self.RMSPlot = TwoDimPlot.TwoDimPlot(self.root, plotName="RMS Plot", xTitle="Epoch", yTitle="RMS Error", closeCallback=self.handleRMSBox)
            self.RMSPlot.addPoints(self.RMSData)
            self.RMSPlot.protocol("WM_DELETE_WINDOW", self.handleRMSBox)
            self.RMSCheck.select()

    def handlePCorrectBox(self):
        if self.pCorrectPlot:
            self.pCorrectPlot.destroy()
            self.pCorrectPlot = None
            self.pCorrectCheck.deselect()
        else:
            self.pCorrectPlot = TwoDimPlot.TwoDimPlot(self.root, plotName="Percent Correct", xTitle="Epoch", yTitle="% Correct", \
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