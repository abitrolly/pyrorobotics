"""

Governor code for self regulating networks.

"""

from pyro.brain.conx import *
from pyro.brain.ravq import ARAVQ, euclideanDistance

class Governor:
    """
    An RAVQ baseclass for combination with Network. 
    """
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
        Returns the index and vector of winning position. Side effect: records
        index of winning pos in histogram.
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

    def saveRAVQ(self, filename):
        """ Saves RAVQ data to a file. """
        self.ravq.saveRAVQToFile(filename)

    def loadRAVQ(self, filename):
        """ Loads RAVQ data from a file. """
        self.ravq.loadRAVQFromFile(filename)

class GovernorNetwork(Governor, Network):
    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6,
                 historySize = 5, alpha = 0.02, mask = [], verbosity = 0):
        # network:
        Network.__init__(self, name = "Governed Network",
                         verbosity = verbosity)
        # ravq
        self.governing = 1
        self.ravq = ARAVQ(bufferSize, epsilon, delta, historySize, alpha) 
        self.ravq.setAddModels(1)
        self.setVerbosity(verbosity)
        self.histogram = {}
        if not mask == []: 
            self.ravq.setMask(mask)

    def setVerbosity(self, val):
        Network.setVerbosity(self, val)
        self.ravq.setVerbosity(val)

    def addThreeLayers(self, i, h, o):
        Network.addThreeLayers(self, i, h, o)
        if not self.ravq.mask:
            sum = float(max(i, h, o))
            mask = [sum/i] * i + [sum/h] * h + [sum/o] * o
            self.ravq.setMask( mask )
            if self.verbosity:
                print "mask:", self.ravq.mask

class GovernorSRN(Governor, SRN): 
    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6,
                 historySize = 5, alpha = 0.02, mask = [], verbosity = 0):
        # network:
        SRN.__init__(self, name = "Governed Acting SRN",
                     verbosity = verbosity)
        self.trainingNetwork = SRN(name = "Governed Training SRN",
                                   verbosity = verbosity)
        self.trainingNetwork.setMomentum(0)
        self.trainingNetwork.setInitContext(0)
        self.setInitContext(0)
        # ravq:
        self.governing = 1
        self.decay = 0
        self.ravq = ARAVQ(bufferSize, epsilon, delta, historySize, alpha) 
        self.ravq.setAddModels(1)
        self.setVerbosity(verbosity)
        self.histogram = {}
        if not mask == []: 
            self.ravq.setMask(mask)

    def setVerbosity(self, val):
        Network.setVerbosity(self, val)
        self.ravq.setVerbosity(val)

    def addThreeLayers(self, i, h, o):
        SRN.addThreeLayers(self, i, h, o)
        self.trainingNetwork.addThreeLayers(i, h, o)
        self.shareWeights(self.trainingNetwork)
        if not self.ravq.mask:
            sum = float(max(i, h, o))
            mask = [sum/i] * i + [sum/h] * h + [sum/o] * o
            self.ravq.setMask( mask )
            if self.verbosity:
                print "mask:", self.ravq.mask

    def sweep(self):
        retval = SRN.sweep(self)
        if self.epoch % self.reportRate == 0:
            print "Model vectors: %d Histogram: %s" %( len(self.ravq.models), self.histogram)
            self.histogram = {}
        if self.decay:
            for i in range(5):
                if len(self.ravq.models.contents):
                    self.ravq.models.contents.pop(0)
                    self.ravq.models.next = (self.ravq.models.next + 1) % \
                                            len(self.ravq.models.contents)
            
            self.next = 0
        return retval

    def networkStep(self, **args):
        if self.governing:
            # map the ravq input context and target
            actContext = list(self["context"].activation)
            vector = list(args["input"]) + actContext + list(args["output"])
            self.map(vector)
            # get the next
            inLen = self["input"].size
            conLen = self["context"].size
            outLen = self["output"].size
            array = self.nextItem()
            if array == None:
                array = vector
            input = array[0:inLen]
            context = array[inLen:inLen+conLen]
            output  = array[inLen+conLen:]
            # load them and train training Network
            self.trainingNetwork.step(input=input,
                                      output=output,
                                      context=context)
        return Network.step(self, **args)
        

if __name__ == '__main__':
    import os, gzip, sys
    # read in 20,000 lines of experimental training data
    locationfile = gzip.open('location.dat.gz', 'r')
    sensorfile = gzip.open('sensors.dat.gz', 'r')
    sensors = sensorfile.readlines()
    locations = locationfile.readlines()
    locationfile.close()
    sensorfile.close()
    # make input/target patterns:
    inputs = []
    for line in sensors:
        inputs.append( map(lambda x: float(x), line.strip().split()))
    targets = []
    for line in locations:
        targets.append( map(lambda x: float(x), line.strip().split()))
    inSize = len(sensors[0].strip().split())
    # Weighting each bank of data equally (except for stalled)
    govMask =  [1] * 16 # 16 sonar sensors
    govMask += [4] * 4  # 4 colors sensors
    govMask += [0] * 1  # 1 stalled sensor
    govMask += [16.0/(inSize/2.0)] * (inSize/2) # context units
    govMask += [4] * 4  # 4 output units
    print "inSize is: ", inSize
    print "govMask is: ", govMask
    print "length is: ", len(govMask)
    # The "16" weights the input determining the multiple labels
    # The choice of epsilon and delta may change the required
    # weights. For binary nodes, changing the value will make the vector
    # distance one from every vector with the opposite value in that
    # node. This change is enough if the delta value is less than
    # one. Use of a high weight value is more to reflect that that
    # node is important in determining the function of the network.
    net = GovernorSRN(5, 2.1, 0.3, 5, 0.2, mask=govMask)
    net.addThreeLayers(inSize, inSize/2, 4)
    net.setTargets( targets[:10000] ) # 389 = one trip around
    net.setInputs( inputs[:10000] )
    net.setStopPercent(.95)
    net.setReportRate(1)
    net.setResetLimit(1)
    net.setTolerance(0.2)
    net.setResetEpoch(2)
    net.governing = int(sys.argv[1])
    print "Goverining is", net.governing
    net.train()
    print net.ravq
    print "Testing..."
    print "This takes a while..."
    net.governing = 0
    net.setTargets( targets )
    net.setInputs( inputs )
    net.setLearning(0)
    tss, correct, total = net.sweep()
    print "TSS: %.4f Percent: %.4f" % (tss, correct / float(total))
    # run with -i to see net

