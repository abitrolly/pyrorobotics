import Tkinter

class ArchDiag(Tkinter.Toplevel):
    SLAB_WIDTH = 200
    SLAB_HEIGHT = 20
    SLAB_VER_SEP = 40
    SLAB_HORIZ_SEP = 20
    LINE_WIDTH = 2
    
    def __init__(self, parent, netStruct):
        Tkinter.Toplevel.__init__(self,parent)
        self.netStruct = netStruct
        self.title("Network Architecture")

        # find the level with the maximum number of layers
        self.maxLayers = 0
        self.netStruct.levelList.reverse()
        for level in netStruct.levelList:
            if len(level) > self.maxLayers:
                self.maxLayers = len(level)

        self.canvasWidth = self.maxLayers*self.SLAB_WIDTH + (self.maxLayers + 1)*self.SLAB_HORIZ_SEP
        self.canvasHeight = len(self.netStruct.levelList)*self.SLAB_HEIGHT + (len(self.netStruct.levelList)+1)*self.SLAB_VER_SEP
        self.diagCanvas = Tkinter.Canvas(self, bg = "white", width=self.canvasWidth, height=self.canvasHeight)
        
        self.coordDict = {}
        self.drawDiag()
        self.diagCanvas.grid(row=0,col=0)

        #connection legend
        legendFrame = Tkinter.Canvas(self)
        blackLineCanvas = Tkinter.Canvas(legendFrame, width=50, height=self.SLAB_HEIGHT)
        blackLineCanvas.create_line(0, self.SLAB_HEIGHT/2, 50, self.SLAB_HEIGHT/2, fill="black", width=2)
        blackLineCanvas.grid(row=0,col=0)
        Tkinter.Label(legendFrame,text="connection").grid(row=0, col=1)
        redLineCanvas = Tkinter.Canvas(legendFrame, width=55, height=self.SLAB_HEIGHT)
        redLineCanvas.create_line(5, self.SLAB_HEIGHT/2, 55, self.SLAB_HEIGHT/2, fill="red", width=2)
        redLineCanvas.grid(row=0,col=2)
        Tkinter.Label(legendFrame,text="context").grid(row=0,col=3)
        legendFrame.grid(row=1,col=0)
        #end connection legend
        
        self.netStruct.levelList.reverse()

        self.update_idletasks()
    def drawDiag(self):
        #place all the vertices and store coordinates in dictionary by name
        verOffset = self.SLAB_VER_SEP
        for level in self.netStruct.levelList:

            horizOffset = (self.canvasWidth - self.SLAB_WIDTH*len(level) - self.SLAB_HORIZ_SEP*(len(level)-1))/2
            for vertex in level:
                self.drawLayer((horizOffset, verOffset), vertex.name, vertex.layerObj.size)
                self.coordDict[vertex.name] = (horizOffset, verOffset)
                horizOffset += self.SLAB_HORIZ_SEP + self.SLAB_WIDTH
            verOffset += self.SLAB_VER_SEP + self.SLAB_HEIGHT

        #add connections by iterating through list again
        for level in self.netStruct.levelList:
            for vertex in level:
                for edge in vertex.edgeOut:
                    self.drawConnection(edge.fromVer.name, edge.toVer.name)
                for edge in vertex.contextIn:
                    self.drawContext(edge.toVer.name, edge.fromVer.name)
                
    def drawLayer(self,posTuple, name, numNodes):
        self.diagCanvas.create_rectangle(posTuple[0], posTuple[1], posTuple[0]+self.SLAB_WIDTH, posTuple[1]+self.SLAB_HEIGHT, \
                                  fill="white", outline="black", width=self.LINE_WIDTH)
        self.diagCanvas.create_text(posTuple[0]+2, posTuple[1]+self.SLAB_HEIGHT/2, fill="black", text=name, anchor=Tkinter.W)
        self.diagCanvas.create_text(posTuple[0]+self.SLAB_WIDTH-2, posTuple[1]+self.SLAB_HEIGHT/2, fill="black", \
                                    text="# Nodes=%u" % (numNodes,), anchor=Tkinter.E)

    def drawConnection(self, fromName, toName):
        fromLoc = self.coordDict[fromName]
        toLoc = self.coordDict[toName]

        if self.sameLevel(fromLoc, toLoc):
            startLoc = self.bottomConnect(fromLoc)
            finishLoc = self.bottomConnect(toLoc)
            self.diagCanvas.create_line(startLoc[0], startLoc[1], \
                                        (startLoc[0]+finishLoc[0])/2, startLoc[1]+self.SLAB_VER_SEP/2,\
                                        finishLoc[0], finishLoc[1], fill="black", arrow=Tkinter.LAST, width=self.LINE_WIDTH, smooth=Tkinter.TRUE)
        else:
            startLoc = self.topConnect(fromLoc)
            finishLoc = self.bottomConnect(toLoc)
            self.diagCanvas.create_line(startLoc[0], startLoc[1], finishLoc[0], finishLoc[1], fill="black", arrow=Tkinter.LAST, width=self.LINE_WIDTH)

    def drawContext(self, fromName, toName):
        startLoc = self.topConnect(self.coordDict[fromName])
        finishLoc = self.topConnect(self.coordDict[toName])
        self.diagCanvas.create_line(startLoc[0], startLoc[1],\
                                    (startLoc[0]+finishLoc[0])/2, startLoc[1]-self.SLAB_VER_SEP/2, \
                                    finishLoc[0], finishLoc[1], fill="red", arrow=Tkinter.LAST, width=self.LINE_WIDTH, smooth=Tkinter.TRUE)
        
    def topConnect(self, tuple):
        return tuple[0]+self.SLAB_WIDTH/2, tuple[1]

    def bottomConnect(self, tuple):
        return tuple[0]+self.SLAB_WIDTH/2, tuple[1]+self.SLAB_HEIGHT

    def sameLevel(self, t1,t2):
        return t1[1] == t2[1]
