"""

Governor code for self regulating networks.

"""

from pyro.brain.conx import *
from pyro.brain.ravq import ARAVQ

class GovernorNetwork(Network):

    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6, historySize = 5, alpha = 0.02,
                 mask = [], verbosity = 0):
        # network:
        Network.__init__(self, name = "Governed Network", verbosity = verbosity)
        # ravq
        self.ravq = ARAVQ(bufferSize, epsilon, delta, historySize, alpha)
        self.ravq.setAddModels(1)
        if not mask == []: 
            self.ravq.setMask(mask)

    def categorize(self, vector):
        self.ravq.input(vector)
        if len(self.ravq.models) == 0:
            return vector
        else:
            return self.ravq.models.nextItem().nextItem()

    def saveRAVQ(self, filename):
        self.ravq.saveRAVQToFile(filename)

    def loadRAVQ(self, filename):
        self.ravq.loadRAVQFromFile(filename)

if __name__ == '__main__':

    import os
    import gzip

    # read in experimental training data
    locationfile = gzip.open('location.dat.gz', 'r')
    sensorfile = gzip.open('sensors.dat.gz', 'r')

    sensors = sensorfile.readlines()
    locations = locationfile.readlines()

    #print "sensors:", sensors[0]
    #print "locations:", locations[0]

    locationfile.close()
    sensorfile.close()

    govEpsilon = 0.2
    delta = 0.8
    alpha = 0.02
    ravqBuffer = 5
    govBuffer = 5

    # The "16" weights the input determining the multiple labels
    
    # The choice of epsilon and delta may change the required
    # weights. For binary nodes, changing the value will make the vector
    # distance one from every vector with the opposite value in that
    # node. This change is enough if the delta value is less than
    # one. Use of a high weight value is more to reflect that that
    # node is important in determining the function of the network.
    
    inSize = len(map(lambda x: float(x), sensors[0].rstrip().split()))
    govMask = [1] * (inSize - 1) + [16] + [inSize/4] * 4
    # create network
    net = GovernorNetwork(ravqBuffer, govEpsilon, delta, govBuffer, alpha, govMask)

    net.addThreeLayers(inSize, inSize/2, 4)
    # the output will code the robots current region

    # defaults - but here explicit
    net.setBatch(0)
    net.setInteractive(0)
    net.setVerbosity(0)
      
    # learning parameters
    net.setEpsilon(0.2)
    net.setMomentum(0.9)
    net.setTolerance(0.05)
    net.setLearning(1)
      
    # initialize network
    net.initialize()
    epochCount = 0
    epochCorrect = 0
    epochTSS = 0
    for i in range(5000): 
        sensorlist = map(lambda x: float(x), sensors[i].rstrip().split())
        locationlist = map(lambda x: float(x), locations[i].rstrip().split())
        array = net.categorize(sensorlist + locationlist)
        error, correct, total = net.step(input = array[:inSize], output = array[inSize:])
        epochTSS += error
        epochCorrect += correct
        epochCount += total
        if i % 100 == 0:
            print "Step: %5d Error: %3.4f Correct: %3.4f" % (i, epochTSS, epochCorrect/float(epochCount))
            epochTSS = 0
            epochCorrect = 0
            epochCount = 0
    print net.ravq
    print "Step: %5d Error: %3.4f Correct: %3.4f" % (i, epochTSS, epochCorrect/float(epochCount))
