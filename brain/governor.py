"""

Governor code for self regulating networks.

"""

from pyro.brain.conx import *
from pyro.brain.ravq import ARAVQ, euclideanDistance

class Governor:
    """
    An RAVQ vitual baseclass for combination with Network. 
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

    def winner(self):
        """
        Get's winning name, m.v. of last winner.
        """
        index = self.ravq.newWinnerIndex
        if index >= 0:
            name = self.ravq.models.names[index]
        else:
            name = index
        return name, self.ravq.winner

    def input(self, vector):
        """
        Wrapper around ravq.input() which returns index and mapped-to m.v. Here, we convert
        index to "name".
        """
        index, modelVector = self.ravq.input(vector)
        if index >= 0:
            name = self.ravq.models.names[index]
        else:
            name = index
        return name, modelVector

    def map(self, vector):
        """
        Returns the index and vector of winning position. Side effect: records
        index of winning pos in histogram and decayHistogram.
        """
        index, modelVector = self.input(vector)
        if self.histogram.has_key(index):
            self.histogram[index] += 1
        else:
            if index >= 0:
                self.histogram[index] = 1
        if self.decayHistogram.has_key(index):
            self.decayHistogram[index] += 1
        else:
            if index >= 0:
                self.decayHistogram[index] = 1
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
        self.decayHistogram = {}
        if not mask == []: 
            self.ravq.setMask(mask)

    def setLearning(self, value):
        self.learning = value
        self.governing = value
        self.ravq.setAddModels(value)

    def setVerbosity(self, val):
        Network.setVerbosity(self, val)
        self.ravq.setVerbosity(val)

    def setMaskWeight(self, iw, ow):
        i = len(self["input"])
        o = len(self["output"])
        parts = []
        if iw:
            parts.append( i/float(iw) )
        else:
            parts.append( 0 )
        if ow:
            parts.append( o/float(ow) )
        else:
            parts.append( 0 )
        sum = float(max(*parts))
        mask = [sum/i * iw] * i + [sum/o * ow] * o
        self.ravq.setMask( mask )
        if self.verbosity:
            print "mask:", self.ravq.mask
 
    def addThreeLayers(self, i, h, o):
        Network.addThreeLayers(self, i, h, o)
        if not self.ravq.mask:
            sum = float(max(i, o))
            mask = [sum/i] * i + [sum/o] * o
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
        self.decayHistogram = {}
        if not mask == []: 
            self.ravq.setMask(mask)

    def setLearning(self, value):
        self.learning = value
        self.governing = value
        self.ravq.setAddModels(value)

    def setVerbosity(self, val):
        Network.setVerbosity(self, val)
        self.ravq.setVerbosity(val)

    def setMaskWeight(self, iw, hw, ow):
        i = len(self["input"])
        h = len(self["hidden"])
        o = len(self["output"])
        parts = []
        if iw:
            parts.append( i/float(iw) )
        else:
            parts.append( 0 )
        if hw:
            parts.append( h/float(hw) )
        else:
            parts.append( 0 )
        if ow:
            parts.append( o/float(ow) )
        else:
            parts.append( 0 )
        sum = float(max(*parts))
        mask = [sum/i * iw] * i + [sum/h * hw] * h + [sum/o * ow] * o
        self.ravq.setMask( mask )
        if self.verbosity:
            print "mask:", self.ravq.mask

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

    def decayModelVectors(self):
        good = []
        goodNames = []
        for name in self.decayHistogram.keys():
            pos = self.ravq.models.names.index(name)
            good.append( self.ravq.models.contents[pos] )
            goodNames.append( self.ravq.models.names[pos] )
        self.decayHistogram = {}
        self.ravq.models.contents = good
        self.ravq.models.names = goodNames
        if len(self.ravq.models.contents):
            self.ravq.models.next = self.ravq.models.next % \
                                    len(self.ravq.models.contents)
        else:
            self.ravq.models.next = 0

    def report(self, hist=1):
        if hist:
            print "Model vectors: %d Histogram: %s" %( len(self.ravq.models), self.histogram)
        else:
            print "Model vectors: %d" %( len(self.ravq.models),)

    def sweep(self):
        retval = SRN.sweep(self)
        if self.governing and (self.epoch % self.reportRate == 0):
            print "Model vectors: %d Histogram: %s" %( len(self.ravq.models), self.histogram)
            self.histogram = {}
        if self.governing and self.decay:
            self.decayModelVectors()
            if self.epoch % self.reportRate == 0:
                print "After decay: Model vectors: %d" % len(self.ravq.models)
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
    net.setSequenceType("epoch")
    net.trainingNetwork.setSequenceType("epoch")
    net.addThreeLayers(inSize, inSize/2, 4)
    net.setTargets( targets[:389] ) # 389 = one trip around
    net.setInputs( inputs[:389] ) # has some pauses in there too
    net.setStopPercent(.95)
    net.setReportRate(1)
    net.setResetLimit(1)
    net.setTolerance(0.2)
    net.governing = int(sys.argv[1])
    net.setResetEpoch(int(sys.argv[2]))
    net.decay = int(sys.argv[3])
    print "Goverining is", net.governing
    print "Decay is", net.decay
    net.train()
    print net.ravq
    print "Decay:", net.decay
    print "Testing..."
    print "This takes a while..."
    net.governing = 0
    net.setTargets( targets )
    net.setInputs( inputs )
    net.setLearning(0)
    tss, correct, total = net.sweep()
    print "TSS: %.4f Percent: %.4f" % (tss, correct / float(total))
    # run with -i to see net
    
