import Queue
#from pyro.brain.conx import *

def genName(edge):
    return "From: %s To: %s" % (edge.fromVer.name, edge.toVer.name)

class Vertex:
    def __init__(self,layerObj):
        self.layerObj = layerObj
        self.edgeOut = []
        self.contextIn = []
        self.visited = 0
        self.name=""
        
    def addEdgeOut(self, newEdge):
        self.edgeOut += [newEdge]

    def addContextIn(self, newCon):
        self.contextIn += [newCon]

    def setName(self, name):
        self.name = name

class Edge:
    def __init__(self,fromVer,toVer,connection):
        self.fromVer = fromVer
        self.toVer = toVer
        self.connection = connection

class NetStruct:
    def __init__(self, network):
        self.network = network
        self.levelList = []
        self.layerDict = {}
        self.edgeList = []
        self.makeLevelList()
        self.nameLevels()
        
    def makeLevelList(self):
        self.levelList = []
        self.edgeList = []
        vertexDict = {}
        inputVertices = []

        # generate vertex list from edge list
        for con in self.network.connections:
            if not vertexDict.has_key(con.toLayer):
                newVertex = Vertex(con.toLayer)
                vertexDict[con.toLayer] = newVertex

            if not vertexDict.has_key(con.fromLayer):
                newVertex = Vertex(con.fromLayer)
                self.edgeList += [Edge(newVertex, vertexDict[con.toLayer], con)]
                newVertex.addEdgeOut(self.edgeList[-1])
                if con.fromLayer.kind[0] == "I":
                    inputVertices += [newVertex]
                vertexDict[con.fromLayer] = newVertex
            else:
                self.edgeList += [Edge(vertexDict[con.fromLayer], vertexDict[con.toLayer], con)]
                vertexDict[con.fromLayer].addEdgeOut(self.edgeList[-1])

            if con.fromLayer.kind[0] == "C":
                vertexDict[con.toLayer].addContextIn(Edge(vertexDict[con.fromLayer], vertexDict[con.toLayer], con))
        
        # modified breadth first search with multiple starting points
        nextLevel = inputVertices
        outputLevel = []

        for vertices in inputVertices:
            vertices.visited = 1
            
        while len(nextLevel) > 0:
            self.levelList += [nextLevel]
            nextLevel = []
            for vertices in self.levelList[-1]:
                for edges in vertices.edgeOut:
                    if not edges.toVer.visited:
                        edges.toVer.visited = 1
                        if edges.toVer.layerObj.kind[0] == "O":
                            outputLevel += [edges.toVer]
                            for contexts in edges.toVer.contextIn:
                                outputLevel += [contexts.fromVer]
                        else:
                            nextLevel += [edges.toVer]
                            for contexts in edges.toVer.contextIn:
                                nextLevel += [contexts.fromVer]
        self.levelList += [outputLevel]

    def nameLevels(self):
        self.layerDict.clear()

        
        #make names for input layers
        if len(self.levelList[0]) == 1:
            self.levelList[0][0].setName("Input")
            self.layerDict[self.levelList[0][0].name] = self.levelList[0][0]
        else:    
            for i in xrange(len(self.levelList[0])):
                self.levelList[0][i].setName("Input %c" % (i+65,))
                self.layerDict[self.levelList[0][i].name] = self.levelList[0][i]

        #make names for hidden and context layers
        for i in xrange(1, len(self.levelList)-1):
            if len(self.levelList[i]) == 1:
                self.levelList[i][0].setName("Hidden %c" % (i+64,))
                self.layerDict[self.levelList[i][0].name] = self.levelList[i][0]
            else:
                if len(self.levelList[i]) == 2 and self.levelList[i][1].layerObj.kind[0] == "C":
                    self.levelList[i][0].setName("Hidden %c" % (64 + i,))
                    self.levelList[i][1].setName("Context for Hidden %c" % (64 + i,))
                else:
                    k = 1
                    for j in xrange(len(self.levelList[i])):
                        if self.levelList[i][j].layerObj.kind[0] == "H":
                            lastHiddenName ="Hidden %c.%c" % (65+j, 96+k)
                            self.levelList[i][j].setName(lastHiddenName)
                            self.layerDict[lastHiddenName] = self.levelList[i][j]
                            k += 1
                        else:
                            self.levelList[i][j].setName("Context for %s" % (lastHiddenName))
                            self.layerDict[self.levelList[i][j].name] = self.levelList[i][j]


        #make names for output layers
        if len(self.levelList[-1]) == 1:
            self.levelList[-1][0].setName("Output")
            self.layerDict[self.levelList[-1][0].name] = self.levelList[-1][0]
        else:    
            for i in xrange(len(self.levelList[-1])):
                self.levelList[-1][i].setName("Output %c" % (65+i,))
                self.layerDict[self.levelList[-1][i].name] = self.levelList[-1][i]

if __name__ == "__main__":
    #n = Network() 
    #n.add(Layer('input',2))
    #n.add(Layer('hidden',2))
    #n.add(Layer('output',1)) 
    #n.connect('input','hidden')
    #n.connect('hidden','output')
    
    #myNetStruct = NetStruct(n)
    #print myNetStruct.levelList
    #print myNetStruct.layerDict
    #print myNetStruct.edgeList

    x = SRN()
    x.addThreeLayers(3,3,3)
    SRNStruct = NetStruct(x)
    print SRNStruct.levelList\

    for layer in x.layers:
        print layer.kind

    for level in SRNStruct.levelList:
        for vertex in level:
            print vertex.name
