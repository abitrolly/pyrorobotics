"""

Governor code for self regulating networks.

"""

from pyro.brain.conx import *
from pyro.brain.ravq import ARAVQ, euclideanDistance

class GovernorNetwork(Network):
    """
    A Network + RAVQ. 
    """
    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6, historySize = 5, alpha = 0.02,
                 mask = [], verbosity = 0):
        # network:
        Network.__init__(self, name = "Governed Network", verbosity = verbosity)
        # ravq
        self.ravq = ARAVQ(bufferSize, epsilon, delta, historySize, alpha) 
        self.ravq.setAddModels(1)
        self.ravq.setVerbosity(verbosity)
        self.histogram = {}
        if not mask == []: 
            self.ravq.setMask(mask)

    def incompatibility(self):
        """
        For each model, how different is it from each of the buffer items? Returns list of
        incompatibilities. Note: uses mask to scale.
        """
        retval = []
        for model in self.ravq.models:
            sum = 0.0
            for buff in model.contents:
                sum += euclideanDistance(model.vector, buff, self.ravq.mask)
            retval.append(sum)
        return retval

    def distancesTo(self, vector):
        """
        Computes euclidean distance from a vector to all model vectors. Note: uses mask
        to scale.
        """
        retval = []
        for m in self.ravq.models:
            retval.append( euclideanDistance(vector, m.vector, self.ravq.mask) )
        return retval

    def map(self, vector):
        """
        Returns the index and vector of winning position. Side effect: records index of winning
        pos in histogram.
        """
        index, modelVector = self.ravq.input(vector)
        if self.histogram.has_key(index):
            self.histogram[index] += 1
        else:
            if index >= 0:
                self.histogram[index] = 1
            # else ignore?
        return (index, modelVector)

    def nextItem(self):
        """ Public interface for getting next item from RAVQ. """
        retval = None
        try:
            retval = self.ravq.models.nextItem().nextItem()
        except AttributeError:
            pass
        return retval

    def __nextitem__(self):
        """ For use in iterable positions:
            >>> govnet = GovernorNetwork()
            >>> for item in govnet:
            ...    print item
            ...
        """
        return self.ravq.models.nextItem().nextItem()

    def categorize(self, vector):
        """
        Maps and gets next item.
        """
        self.map(vector)
        if len(self.ravq.models) == 0:
            return vector
        else:
            return self.nextItem()

    def saveRAVQ(self, filename):
        """ Saves RAVQ data to a file. """
        self.ravq.saveRAVQToFile(filename)

    def loadRAVQ(self, filename):
        """ Loads RAVQ data from a file. """
        self.ravq.loadRAVQFromFile(filename)

if __name__ == '__main__':
    import os, gzip

    # read in experimental training data
    locationfile = gzip.open('location.dat.gz', 'r')
    sensorfile = gzip.open('sensors.dat.gz', 'r')
    sensors = sensorfile.readlines()
    locations = locationfile.readlines()
    locationfile.close()
    sensorfile.close()

    govEpsilon = 0.2
    delta = 0.8
    alpha = .9 # 0.02
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
    #govMask = [1] * (inSize - 1) + [0] + [inSize/4] * 4
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
    totalSteps = 0
    lastNumberOfModelVectors = 0
    for sweeps in range(1):
        epochCount = 0
        epochCorrect = 0
        epochTSS = 0
        for i in range(5000):  # about 80 is one room; loops about every 410
            sensorlist = map(lambda x: float(x), sensors[i].rstrip().split())
            locationlist = map(lambda x: float(x), locations[i].rstrip().split())
            #array = sensorlist + locationlist
            index, modelVector = net.map(sensorlist + locationlist)
            #array = net.categorize(sensorlist + locationlist)
            array = net.nextItem()
            if array == None:
                array = sensorlist + locationlist
            error, correct, total = net.step(input = array[:inSize], output = array[inSize:])
            epochTSS += error
            epochCorrect += correct
            epochCount += total
            if lastNumberOfModelVectors != len(net.ravq.models):
                print "*" * 50, "New model vector!"
                print "Distances from new model vector at all others:"
                print ["%.2f" % v for v in net.distancesTo( net.ravq.winner )]
                print "*" * 50
                lastNumberOfModelVectors = len(net.ravq.models)
            if (totalSteps+1) % 80 == 0 or totalSteps == 5000 - 1:
                print "-" * 50
                print "Step: %5d Error: %9.4f Correct: %9.4f" % (totalSteps+1, epochTSS, epochCorrect/float(epochCount))
                print "Histogram:", net.histogram
                net.histogram = {}
                epochTSS = 0
                epochCorrect = 0
                epochCount = 0
            totalSteps += 1
        print net.ravq
        print "Distance map:\n"
        print net.ravq.distanceMapAsString()
        print "*" * 50

# plot map with: gnuplot: splot "datafile" matrix with pm3d
