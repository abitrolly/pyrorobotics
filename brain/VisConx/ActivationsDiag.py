import Tkinter
import copy
import math

class LayerCanvas(Tkinter.Canvas):
    PADDING = 4
    def __init__(self, parent, numNodes, numColumns=3, nodeSize=25):
        #calculate dimensions
        self.numColumns = numColumns
        self.numRows = int(math.ceil(float(numNodes)/numColumns))
        self.nodeSize = nodeSize
        self.numNodes = numNodes
        self.plotWidth = numColumns*nodeSize + (numColumns+1)*self.PADDING
        self.plotHeight = self.numRows*nodeSize + (self.numRows + 1)*self.PADDING

        #create canvas
        Tkinter.Canvas.__init__(self, parent, height=self.plotHeight, width=self.plotWidth, bg = "white")

        #draw nodes
        self.nodeItems = []
        for i in xrange(numNodes):
            coords = self.nodeNumToCoords(i)
            self.nodeItems += [self.create_oval(coords[0], coords[1], coords[0]+nodeSize, coords[1]+nodeSize, outline="black")]

    def nodeNumToCoords(self, nodeNum):
        xCoord = (nodeNum//self.numRows)*(self.nodeSize + self.PADDING) + self.PADDING
        yCoord = (nodeNum % self.numRows)*(self.nodeSize + self.PADDING) + self.PADDING

        return xCoord, yCoord
    
    def updateActivs(self, newActivs):
        for i in xrange(len(self.nodeItems)):
            self.itemconfigure(self.nodeItems[i], fill ="#%04x%04x%04x" % ((65535*newActivs[i],)*3))

    def getWidth(self):
        return self.plotWidth

class LevelFrame(Tkinter.Frame):
    def __init__(self, parent, layerTupleList):
        Tkinter.Frame.__init__(self, parent)
        self.nameNumList = layerTupleList
        self.layerCanvasList = []

        for nameNumTuple in self.nameNumList:
            Tkinter.Label(self, text=nameNumTuple[0]).pack()
            self.layerCanvasList += [LayerCanvas(self, nameNumTuple[1], numColumns=3, nodeSize=25)]
            self.layerCanvasList[-1].pack()

    def updateActivs(self, newActivs):
        for i in xrange(len(self.layerCanvasList)):
            self.layerCanvasList[i].updateActivs(newActivs[i])

    def getWidth(self):
        return self.layerCanvasList[0].getWidth()
    
class ActivDiag(Tkinter.Toplevel):
    def __init__(self, parent, netStruct):
        Tkinter.Toplevel.__init__(self, parent)
        self.netStruct=netStruct
        self.levelFrameList = []
        self.desOutputFrame = None
        self.currentIndex = 0
        self.storedActivs= []
        
        #create the level frames
        for i in xrange(len(self.netStruct.levelList)):
            layerTupleList = [(vertex.name, vertex.layerObj.size) for vertex in self.netStruct.levelList[i]]
            self.levelFrameList += [LevelFrame(self, layerTupleList)]
            self.levelFrameList[i].grid(row=0, column=i)
        layerTupleList = [("Desired %s" % (layer[0],), layer[1]) for layer in layerTupleList]
        self.levelFrameList += [LevelFrame(self, layerTupleList)]
        self.levelFrameList[-1].grid(row=0, column=len(self.netStruct.levelList))
        
        #make grayscale ramp
        SCALE_HEIGHT = 20
        plotWidth = 0
        for level in self.levelFrameList:
            plotWidth += level.getWidth()
        scaleCanvas = Tkinter.Canvas(self, height=SCALE_HEIGHT, width=plotWidth)
        for i in xrange(plotWidth):
            scaleCanvas.create_line(i, 0, i, SCALE_HEIGHT, fill="#%04x%04x%04x" % ((65535*float(i)/(plotWidth-1),)*3))
        scaleCanvas.create_text(0, SCALE_HEIGHT/2, text="0.0", fill="red", anchor = Tkinter.W)
        scaleCanvas.create_text(plotWidth-1, SCALE_HEIGHT/2, text="1.0", fill="red", anchor = Tkinter.E)
        scaleCanvas.grid(row=1, column=0, columnspan=len(self.levelFrameList)+1)
        
        #make prev/next buttons
        buttonFrame = Tkinter.Frame(self)
        self.prevButton = Tkinter.Button(buttonFrame, text="Previous", command=self.handlePrev)
        self.prevButton.pack(side=Tkinter.LEFT)
        self.nextButton = Tkinter.Button(buttonFrame, text="Next", command=self.handleNext)
        self.nextButton.pack(side=Tkinter.LEFT)
        buttonFrame.grid(row=2, column=0, columnspan=len(self.levelFrameList)+1)

        self.calcActivs()
        self.drawActivs()

    def calcActivs(self):
        #this is ugly, but essential to the extraction of data from sweep
        self.netStruct.network.activDiag = self
        self.netStruct.network.sweep()
        
    def extractActivs(self):
        currentPattern = []
        for level in self.netStruct.levelList:
            currentLevel =[]
            for vertex in level:
                currentLevel += [copy.deepcopy(vertex.layerObj.activation)]
            currentPattern += [currentLevel]
        currentLevel = []
        for vertex in self.netStruct.levelList[-1]:
            currentLevel += [copy.deepcopy(vertex.layerObj.target)]
        currentPattern += [currentLevel]
        self.storedActivs += [currentPattern]
        
    def handleNext(self):
        self.currentIndex += 1
        self.prevButton.config(state=Tkinter.NORMAL)
        if self.currentIndex ==  len(self.storedActivs)-1:
            self.nextButton.config(state=Tkinter.DISABLED)
        
        self.drawActivs()
        
    def handlePrev(self):
        self.currentIndex -= 1
        self.nextButton.config(state=Tkinter.NORMAL)
        if self.currentIndex == 0:
            self.prevButton.config(state=Tkinter.DISABLED)

        self.drawActivs()

    def drawActivs(self):
        for i in xrange(len(self.levelFrameList)):
            self.levelFrameList[i].updateActivs(self.storedActivs[self.currentIndex][i])
        self.update_idletasks()
