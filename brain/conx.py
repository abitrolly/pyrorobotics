# Proposed changes

# Standalone functions:
#    Fixed randomArray to return values in proper range
# In Network class:
#    Added a class variable called prediction which operates like association
#    Added a method predict which operates like associate to do prediction
#    Updated preprop to process predictions
#    Updated preprop to pass step*length of pattern to loading methods
#    Updated loadTarget to include start in the call to copyVector
#    Added a class variable called resetLimit
#    Added a method setResetLimit
#    Updated train to check when resetCount==resetLimit and stops training
#    Removed associationCount, not used and can be determined from length
#    Added a class variable orderedInput, when this is true should not
#      randomize the order of the inputs
#    Added a method setOrderedInput
#    Updated sweep method to include an if check for orderedInput
#    Updated sweep method to move postprop call--was not showing correct
#      context layer values due to its placement
# In SRN class:
#    Added a method addSRNLayers
#    Updated preprop to check if sequenceLength>1 before initializing context
#    Updated postprop to always copy hidden to context

# ------------------------------------------------
# An Artificial Neural Network System Implementing
# Backprop, and Quickprop
# ------------------------------------------------
# (c) 2001-2002, D.S. Blank, Bryn Mawr College
# ------------------------------------------------

import RandomArray, Numeric, math, random, time, sys, signal

version = "5.6"

def randomArray(size, max):
    """
    Returns an array initialized to random values between -max and max
    """
    temp = RandomArray.random(size) * 2 * max
    return temp - max

def displayArray(name, a, width = 0):
    print name + ": "
    cnt = 0
    for i in a:
        print "%4.1f" % i,
        if width > 0 and (cnt + 1) % width == 0:
            print ''
        cnt += 1
    #print ""

def writeArray(fp, a):
    for i in a:
        fp.write("%f " % i)
    fp.write("\n")

class Layer:
    """
    Class which contains arrays of node elements (ie, activation,
    error, bias, etc)
    """
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.displayWidth = size
        self.type = 'Input' # determined by connectivity
        self.verbosity = 0
        self.log = 0
        self.logFile = ''
        self._logPtr = 0
        self.bepsilon = 0.1
        self.initialize()
    def initialize(self):
        self.randomize()
        self.target = Numeric.zeros(self.size, 'f')
        self.error = Numeric.zeros(self.size, 'f')
        self.activation = Numeric.zeros(self.size, 'f')
        self.bias_slope = Numeric.zeros(self.size, 'f')
        self.bias_prevslope = Numeric.zeros(self.size, 'f')
        self.dbias = Numeric.zeros(self.size, 'f')
        self.delta = Numeric.zeros(self.size, 'f')
        self.netinput = Numeric.zeros(self.size, 'f')
        self.bed = Numeric.zeros(self.size, 'f')
    def getWinner(self, type = 'activation'):
        maxvalue = -10000
        maxpos = -1
        ttlvalue = 0
        if type == 'activation':
            for i in range(self.size):
                ttlvalue += self.activation[i]
                if self.activation[i] > maxvalue:
                    maxvalue = self.activation[i]
                    maxpos = i
        elif type == 'target':
            for i in range(self.size):
                ttlvalue += self.target[i]
                if self.target[i] > maxvalue:
                    maxvalue = self.target[i]
                    maxpos = i
        if self.size > 0:
            avgvalue = ttlvalue / float(self.size)
        else:
            avgvalue = 0.0
        return maxpos, maxvalue, avgvalue
    def setLog(self, fileName):
        self.log = 1
        self.logFile = fileName
        self._logPtr = open(fileName, "w")
    def logMsg(self, msg):
        self._logPtr.write(msg)
    def closeLog(self):
        self._logPtr.close()
        self.log = 0
    def writeLog(self):
        if self.log:
            writeArray(self._logPtr, self.activation)
    def setDisplayWidth(self, val):
        self.displayWidth = val
    def randomize(self):
        self.bias = randomArray(self.size, 0.4)
    def display(self):
        print "============================="
        print "Display Layer '" + self.name + "' (type " + self.type + "):"
        if (self.type == 'Output'):
            displayArray('Target', self.target, self.displayWidth)
        displayArray('Activation', self.activation, self.displayWidth)
        if (self.type != 'Input' and self.verbosity > 0):
            displayArray('Error', self.error, self.displayWidth)
        if (self.verbosity > 4 and self.type != 'Input'):
            print "    ", ; displayArray('bias', self.bias)
            print "    ", ; displayArray('bias_slope', self.bias_slope)
            print "    ", ; displayArray('bias_prevslope', self.bias_prevslope)
            print "    ", ; displayArray('dbias', self.dbias)
            print "    ", ; displayArray('delta', self.delta)
            print "    ", ; displayArray('netinput', self.netinput)
            print "    ", ; displayArray('bed', self.bed)
    def setActivations(self, value):
        for i in range(self.size):
            self.activation[i] = value
    def copyActivations(self, arr):
        for i in range(self.size):
            self.activation[i] = arr[i]
    def copyTarget(self, arr):
        for i in range(self.size):
            self.target[i] = arr[i]

# A neural Network connection between layers

class Connection:
    """
    Class which contains pointers to two layers (from and to) and the
    weights between them.
    """
    def __init__(self, fromLayer, toLayer):
        self.epsilon = 0.1
        self.split_epsilon = 0
        self.fromLayer = fromLayer
        self.toLayer = toLayer
        self.initialize()
    def initialize(self):
        self.randomize()
        self.dweight = Numeric.zeros((self.toLayer.size, \
                                           self.fromLayer.size), 'f')
        self.wed = Numeric.zeros((self.toLayer.size, \
                                  self.fromLayer.size), 'f')
        self.slope = Numeric.zeros((self.toLayer.size, \
                                    self.fromLayer.size), 'f')
        self.prevslope = Numeric.zeros((self.toLayer.size, \
                                        self.fromLayer.size), 'f')
    def display(self):
        print "Weights: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'"
        print "             ",
        for i in range(self.toLayer.size):
            print self.toLayer.name, "[", i, "]",
        print ''
        for i in range(self.fromLayer.size):
            print self.fromLayer.name, "[", i, "]", ": ",
            for j in range(self.toLayer.size):
                print self.weight[j][i],
            print ''
        print ''
    def setEpsilon(self, value):
        self.epsilon = value
        self.bepsilon = value
    def setSplitEpsilon(self, value):
        self.split_epsilon = value
    def getEpsilon(self):
        if (self.split_epsilon):
            return (self.epsilon / self.fromLayer.size)
        else:
            return self.epsilon
    def randomize(self):
        self.weight = randomArray((self.toLayer.size, \
                                   self.fromLayer.size), 0.4)

# A neural Network

class Network:
    """
    Class which contains all of the parameters and methods needed to
    run a neural network.
    """
    def __init__(self, name = 'Backprop Network', verbosity = 0):
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.name = name
        self.layer = []
        self.layerCount = 0
        self.layerByName = {}
        self.connection = []
        self.connectionCount = 0
        self.inputMap = []
        self.inputMapCount = 0
        self.outputMap = []
        self.outputMapCount = 0
        self.prediction = []
        self.association = []
        self.input = []
        self.output = []
        self.orderedInput = 0
        self.loadOrder = []
        self.learning = 1
        self.momentum = 0.9
        self.resetEpoch = 1000
        self.resetCount = 0
        self.resetLimit = 1
        self.sequenceLength = 1
        self.autoSequence = 1 # auto detect length of sequence from input size
        self.batch = 0
        self.learnDuringSequence = 0
        self.verbosity = verbosity
        self.stopPercent = 1.0
        self.sigmoid_prime_offset = 0.1
        self.qp_decay = -0.0001
        self.qp_mode_threshold = 0.0
        self.symmetric = 0
        self.qp_mu = 1.75
        self.qp_mode = 0
        self.tolerance = 0.4
        self.interactive = 0
        self.epsilon = 0.1
        self.learning = 1
        self.reportRate = 25
    def arrayify(self):
        gene = []
        for lay in self.layer:
            if lay.type != 'Input':
                for i in range(lay.size):
                    gene.append( lay.bias[i] )
        for con in self.connection:
            for j in range(con.fromLayer.size):
                for i in range(con.toLayer.size):
                    gene.append( con.weight[i][j] )
        return gene
    def unArrayify(self, gene):
        g = 0
        for lay in self.layer:
            if lay.type != 'Input':
                for i in range(lay.size):
                    lay.bias[i] = float( gene[g])
                    g += 1
        for con in self.connection:
            for j in range(con.fromLayer.size):
                for i in range(con.toLayer.size):
                    con.weight[i][j] = gene[g]
                    g += 1
    def setOrderedInput(self, value):
        self.orderedInput = value
    def setInteractive(self, value):
        self.interactive = value
    def setAutoSequence(self, value):
        self.autoSequence = value
    def setSequenceLength(self, value):
        self.sequenceLength = value
    def setSymmetric(self, value):
        self.symmetric = value
    def setTolerance(self, value):
        self.tolerance = value
    def setLearning(self, value):
        self.learning = value
    def setMomentum(self, value):
        self.momentum = value
    def setResetLimit(self, value):
        self.resetLimit = value
    def setResetEpoch(self, value):
        self.resetEpoch = value
    def setBatch(self, value):
        self.batch = value
    def setLearnDuringSequence(self, value):
        self.learnDuringSequence = value
    def reset(self):
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))
        self.initialize()
    def setSeed(self, value):
        self.seed1 = value
        self.seed2 = value / 23.45
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))
    def setInputs(self, inputs):
        self.input = inputs
        self.loadOrder = range(len(self.input)) # not random
        # will randomize later, if need be
    def initialize(self):
        for c in range(self.connectionCount):
            self.connection[c].initialize()
        for i in range(self.layerCount):
            self.layer[i].initialize()
    def randomizeOrder(self):
        flag = [0] * len(self.input)
        self.loadOrder = [0] * len(self.input)
        for i in range(len(self.input)):
            pos = int(random.random() * len(self.input))
            while (flag[pos] == 1):
                pos = int(random.random() * len(self.input))
            flag[pos] = 1
            self.loadOrder[pos] = i
    def setEpsilon(self, value):
        self.epsilon = value
        for c in range(self.connectionCount):
            self.connection[c].setEpsilon(value)
    def ce_init(self):
        retval = 0.0; correct = 0; totalCount = 0
        for x in range(self.layerCount):
            if (self.layer[x].type == 'Output'):
                for t in range(self.layer[x].size):
                    self.layer[x].error[t] = self.diff(self.layer[x].target[t] - self.layer[x].activation[t])
                    if (math.fabs(self.layer[x].error[t]) < self.tolerance):
                        correct += 1
                    totalCount += 1
                    retval += (self.layer[x].error[t] ** 2)
        return (retval, correct, totalCount)
    def compute_error(self):
        error, correct, total = self.ce_init()
        # go backwards through each proj
        for x in range(self.connectionCount - 1, -1, -1):
            # but don't redo output errors!
            self.ce_process(self.connection[x])
        return (error, correct, total)
    def ce_process(self, connect):
        for i in range(connect.toLayer.size):
            # could put this in ce_init, do just once per layer,
            # doesn't hurt though
            connect.toLayer.delta[i] = connect.toLayer.error[i] * \
                                       self.ACTPRIME(connect.toLayer.activation[i])
            # FIX? do I need to update to->bias_slope[i] here?
            for j in range(connect.fromLayer.size):
                connect.fromLayer.error[j] += (connect.toLayer.delta[i] * connect.weight[i][j])
                connect.slope[i][j] += (connect.toLayer.delta[i] * connect.fromLayer.activation[j])
                connect.toLayer.bias_slope[i] += (connect.toLayer.delta[i] * connect.fromLayer.activation[j])
    def ACTPRIME(self, act):
        if self.symmetric:
            return ((0.25 - act * act) + self.sigmoid_prime_offset)
        else:
            return ((act * (1.0 - act)) + self.sigmoid_prime_offset)
    def cw_process(self, connect):
        for i in range(connect.toLayer.size):
            for j in range(connect.fromLayer.size):
                connect.wed[i][j] = connect.wed[i][j] + (connect.toLayer.delta[i] * connect.fromLayer.activation[j])
    def compute_wed(self):
        for x in range(self.connectionCount):
            self.cw_process( self.connection[x] )
        for x in range(self.layerCount):
            for i in range(self.layer[x].size):
                self.layer[x].bed[i] += self.layer[x].delta[i]
    def diff(self, value):
        if math.fabs(value) < 0.1:
            return 0.0
        else:
            return value
    def copyVector(self, vector1, vector2, start):
        length = min(len(vector1), len(vector2))
        if self.verbosity > 1:
            print "Copying Vector: ", vector2[start:start+length]
        if self.symmetric:
            p = 0
            for i in range(start, start + length):
                vector1[p] = vector2[i] - 0.5
                p += 1
        else:
            p = 0
            for i in range(start, start + length):
                vector1[p] = vector2[i]
                p += 1
    def loadInput(self, pos, start = 0):
        if pos >= len(self.input):
            return
        if self.verbosity > 0: print "Loading input", pos, "..."
        if self.inputMapCount == 0:
            self.copyVector(self.layer[0].activation, self.input[pos], start)
        else: # mapInput set manually
            for vals in self.inputMap:
                (v1, offset) = vals
                self.copyVector(self.getLayer(v1).activation, \
                                self.input[pos], offset)
    def loadTarget(self, pos, start = 0):
        if pos >= len(self.output):
            return
        if self.verbosity > 1: print "Loading target", pos, "..."
        if self.outputMapCount == 0:
            self.copyVector(self.layer[self.layerCount-1].target, \
                            self.output[pos], start)
        else: # mapOutput set manually
            for vals in self.outputMap:
                (v1, offset) = vals
                self.copyVector(self.getLayer(v1).target,
                                self.output[pos], offset)
    def init_slopes(self):
        for x in range(self.connectionCount):
            for i in range(self.connection[x].toLayer.size):
                self.connection[x].toLayer.bias_prevslope[i] = self.connection[x].toLayer.bias_slope[i]
                self.connection[x].toLayer.bias_slope[i] = self.qp_decay * self.connection[x].toLayer.bias[i]
                for j in range(self.connection[x].fromLayer.size):
                    self.connection[x].prevslope[i][j] = self.connection[x].slope[i][j]
                    self.connection[x].slope[i][j] = self.qp_decay * self.connection[x].weight[i][j]
    def train(self):
        tssErr = 1.0; e = 1; totalCorrect = 0; totalCount = 1;
        #totalPatterns = len(self.output) * len(self.input[0]) /
        #self.layer[0].size
        self.resetCount = 0
        while totalCount != 0 and \
              totalCorrect * 1.0 / totalCount < self.stopPercent:
            (tssErr, totalCorrect, totalCount) = self.sweep()
            if e % self.reportRate == 0:
                print "Epoch #%6d" % e, "| TSS Error: %.2f" % tssErr, \
                      "| Correct =", totalCorrect * 1.0 / totalCount
            if self.resetEpoch == e:
                if self.resetCount == self.resetLimit:
                    print "Reset limit reached; ending without reaching goal"
                    break
                self.resetCount += 1
                print "RESET! resetEpoch reached; starting over..."
                self.initialize()
                tssErr = 1.0; e = 1; totalCorrect = 0
                continue
            e += 1
        print "----------------------------------------------------"
        if totalCount > 0:
            print "Final #%6d" % e, "| TSS Error: %.2f" % tssErr, \
                  "| Correct =", totalCorrect * 1.0 / totalCount
        else:
            print "Final: nothing done"
        print "----------------------------------------------------"
    def cycle(self):
        return self.sweep()
    def preprop(self, pattern, step):
        self.loadInput(pattern, step*self.layer[0].size)
        self.loadTarget(pattern, step*self.layer[self.layerCount-1].size)
        for aa in self.association:
            (inName, outName) = aa
            inLayer = self.getLayer(inName)
            outLayer = self.getLayer(outName)
            outLayer.copyTarget(inLayer.activation)
        for p in self.prediction:
            (inName, outName) = p
            inLayer = self.getLayer(inName)
            outLayer = self.getLayer(outName)
            if self.sequenceLength == 1:
                position = (pattern + 1) % len(self.input)
                outLayer.copyTarget(self.input[position])
            else:
                start = ((step + 1) * inLayer.size) % len(self.input[pattern])
                self.copyVector(outLayer.target, self.input[pattern], start)
    def postprop(self, pattern, sequence):
        pass
    def sweep(self):
        if self.verbosity > 0: print "Cycle..."
        if not self.orderedInput:
            self.randomizeOrder()
        self.init_slopes() # here, doing batch?
        tssError = 0.0; totalCorrect = 0; totalCount = 0;
        for i in self.loadOrder:
            if self.autoSequence:
                self.sequenceLength = len(self.input[i]) / self.layer[0].size
            if self.verbosity > 0 or self.interactive:
                print "-----------------------------------Pattern #", i + 1
            for s in range(self.sequenceLength):
                if self.verbosity > 0 or self.interactive:
                    print "Step #", s + 1
                self.preprop(i, s)
                self.propagate()
                if (s + 1 < self.sequenceLength and not self.learnDuringSequence):
                    pass # don't update error or count
                else:
                    (error, correct, total) = self.backprop() # compute_error()
                    tssError += error
                    totalCorrect += correct
                    totalCount += total
                if self.verbosity > 0 or self.interactive:
                    self.display()
                    if self.interactive:
                        print "--More-- [quit, go] ",
                        chr = sys.stdin.readline()
                        if chr[0] == 'g':
                            self.interactive = 0
                        elif chr[0] == 'q':
                            sys.exit(1)
                # the following could be in this loop, or not
                self.postprop(i, s)
                if self.sequenceLength > 1:
                    if self.learning and self.learnDuringSequence:
                        self.change_weights()
                # else, do nothing here
            if self.sequenceLength > 1:
                if self.learning and not self.learnDuringSequence:
                    self.change_weights()
            else:
                if self.learning and not self.batch:
                    self.change_weights()
        if self.sequenceLength == 1:
            if self.learning and self.batch:
                self.change_weights() # batch
        return (tssError, totalCorrect, totalCount)
    def reset_error(self):
        for x in range(self.layerCount):
            for i in range(self.layer[x].size):
                self.layer[x].error[i] = 0.0
    def setOutputs(self, outputs):
        self.output = outputs
    def activationFunction(self, x):
        if (x > 15.0):
            retval = 1.0
        elif (x < -15.0):
            retval = 0.0
        else:
            try:
                retval = (1.0 / (1.0 + math.exp(-x)))
            except OverflowError:
                retval = 0.0
        if self.symmetric:
            return retval - 0.5
        else:
            return retval
    def add(self, layer, verbosity = 0):
        layer.verbosity = verbosity
        self.layer.append(layer)
        self.layerByName[layer.name] = layer
        self.layerCount += 1
    def logMsg(self, layerName, message):
        self.getLayer(layerName).logMsg(message)
    def logLayer(self, layerName, fileName):
        self.getLayer(layerName).setLog(fileName)
    def connect(self, fromName, toName):
        fromLayer = self.getLayer(fromName)
        toLayer   = self.getLayer(toName)
        if (fromLayer.type == 'Output'):
            fromLayer.type = 'Hidden'
        if (toLayer.type == 'Input'):
            toLayer.type = 'Output'
        self.connection.append(Connection(fromLayer, toLayer))
        self.connection[self.connectionCount].setEpsilon(self.epsilon)
        self.connectionCount += 1
    def associate(self, inName, outName):
        self.association.append((inName, outName))
    def predict(self, inName, outName):
        self.prediction.append((inName, outName))
    def mapInput(self, vector1, offset = 0):
        self.inputMap.append((vector1, offset))
        self.inputMapCount += 1
    def mapOutput(self, vector1, offset = 0):
        self.outputMap.append((vector1, offset))
        self.outputMapCount += 1
    def propagate(self, propfrom = 0):
        if self.verbosity > 2: print "Propagate Network '" + self.name + "':"
        # Initialize netinput:
        for n in range(propfrom, self.layerCount):
            if (self.layer[n].type != 'Input'):
                for i in range(self.layer[n].size):
                    self.layer[n].netinput[i] = self.layer[n].bias[i]
        # For each connection, in order:
        for n in range(propfrom, self.layerCount):
            for c in range(self.connectionCount):
                if (self.connection[c].toLayer.name == self.layer[n].name):
                    self.prop_process(self.connection[c]) # propagate!
            if (self.layer[n].type != 'Input'):
                for i in range(self.layer[n].size):
                    self.layer[n].activation[i] = self.activationFunction(self.layer[n].netinput[i])
        for n in range(propfrom, self.layerCount):
            if self.layer[n].log:
                self.layer[n].writeLog()
    def prop_process(self, connect):
        if self.verbosity > 5:
            print "Prop_process from " + connect.fromLayer.name + " to " + \
                  connect.toLayer.name
        for i in range(connect.toLayer.size):
            if self.verbosity > 6: print "netinput@", connect.toLayer.name, "starts at", connect.toLayer.netinput[i]
            for j in range(connect.fromLayer.size):
                if self.verbosity > 6: print "netinput@", connect.toLayer.name, "[", i, "] = ", connect.fromLayer.activation[j], "*", connect.weight[i][j]
                connect.toLayer.netinput[i] += (connect.fromLayer.activation[j] * connect.weight[i][j])
                if self.verbosity > 6: print "netinput@", connect.toLayer.name, "[", i, "] = ", connect.toLayer.netinput[i]
    def backprop(self):
        self.reset_error()
        retval = self.compute_error()
        self.compute_wed()
        return retval
    def change_weights(self):
        qp_shrink_factor = self.qp_mu / (1.0 + self.qp_mu);
        for l in range(self.connectionCount):
            for i in range(self.connection[l].toLayer.size):
                for j in range(self.connection[l].fromLayer.size):
                    nextstep = 0.0
                    if self.qp_mode and self.connection[l].dweight[i][j] > self.qp_mode_threshold:
                        if (self.connection[l].slope[i][j] > 0.0):
                            nextstep += (self.connection[l].getEpsilon() * self.connection[l].slope[i][j])
                        if (self.connection[l].slope[i][j] > (qp_shrink_factor * self.connection[l].prevslope[i][j])):
                            nextstep += (self.qp_mu * self.connection[l].dweight[i][j])
                        else:
                            try:
                                nextstep += ((self.connection[l].slope[i][j] / \
                                              (self.connection[l].prevslope[i][j] - self.connection[l].slope[i][j])) \
                                             * self.connection[l].dweight[i][j])
                            except: # Divide by Zero
                                nextstep = 0.0
                        self.connection[l].dweight[i][j] = nextstep
                    elif (self.qp_mode and self.connection[l].dweight[i][j] < -self.qp_mode_threshold):
                        if (self.connection[l].slope[i][j] < 0.0):
                            nextstep += (self.connection[l].getEpsilon() * self.connection[l].slope[i][j])
                        if (self.connection[l].slope[i][j] < (qp_shrink_factor * self.connection[l].prevslope[i][j])):
                            nextstep += (self.qp_mu * self.connection[l].dweight[i][j])
                        else:
                            try:
                                nextstep += ((self.connection[l].slope[i][j] / \
                                              (self.connection[l].prevslope[i][j] - self.connection[l].slope[i][j])) \
                                             * self.connection[l].dweight[i][j])
                            except:
                                nextstep = 0.0
                        self.connection[l].dweight[i][j] = nextstep
                    else:
                        self.connection[l].dweight[i][j] = self.connection[l].getEpsilon() * self.connection[l].wed[i][j] + \
                                                           self.momentum * self.connection[l].dweight[i][j]
                    self.connection[l].weight[i][j] += self.connection[l].dweight[i][j]
                    self.connection[l].wed[i][j] = 0.0
        for l in range(self.layerCount):
            for i in range(self.layer[l].size):
                self.layer[l].dbias[i] = self.layer[l].bepsilon * self.layer[l].bed[i] + self.momentum * self.layer[l].dbias[i]
                self.layer[l].bias[i] += self.layer[l].dbias[i]
                self.layer[l].bed[i] = 0.0
    def getLayer(self, name):
        return self.layerByName[name]
    def getWeights(self, fromName, toName):
        for i in range(self.connectionCount):
            if self.connection[i].fromLayer.name == fromName and \
               self.connection[i].toLayer.name == toName:
                return self.connection[i].weight
    def display(self, seeWeights = 0):
        print "Display network '" + self.name + "':"
        size = range(self.layerCount)
        size.reverse()
        for i in size:
            self.layer[i].display()
            weights = range(self.connectionCount)
            weights.reverse()
            if seeWeights:
                for j in weights:
                    if self.connection[j].toLayer.name == self.layer[i].name:
                        self.connection[j].display()
    def addThreeLayers(self, inc, hidc, outc):
        self.add( Layer('input', inc) )
        self.add( Layer('hidden', hidc) )
        self.add( Layer('output', outc) )
        self.connect('input', 'hidden')
        self.connect('hidden', 'output')
    def saveNetworkToFile(self, filename, saveData = 1):
        print "Error: FIX doesn't save postprop() or preprop() code! Pickle?"
        basename = filename.split('.')[0]
        filename += ".py"
        if saveData:
            self.saveDataToFile(basename + ".dat")
        # save a description (python code?) (.py)
        fp = open(filename, 'w')
        fp.writelines("# This file was automatically created.\n\n")
        fp.writelines("# Con-x: Sample XOR Network\n")
        fp.writelines("# (c) 2001, D.S. Blank\n")
        fp.writelines("# Bryn Mawr College\n")
        fp.writelines("# http://emergent.brynmawr.edu/\n\n")
        fp.writelines("from pyro.brain.conx import *\n\n")
        fp.writelines("# Create network:\n")
        fp.writelines("net = Network()\n")
        fp.writelines("# Set the network parameters:\n")
        for i in dir(self):
            if i.find("Count") >= 0 or i.find("_") == 0:
                # skip it
                continue
            if type(eval("self.%s" % i)) == type(1.2):
                methodName =  "%s" % i
                methodName = methodName[0].upper() + methodName[1:]
                fp.writelines("net.set%s(%f)\n" % \
                              (methodName, eval("self.%s" % i)))
            if type(eval("self.%s" % i)) == type(1):
                methodName =  "%s" % i
                methodName = methodName[0].upper() + methodName[1:]
                fp.writelines("net.set%s(%d)\n" % \
                              (methodName, eval("self.%s" % i)))
        fp.writelines("net.setSeed(net.seed1)\n")
        fp.writelines("# Create the layers:\n")
        for layer in self.layer:
            fp.writelines("net.add( Layer('%s', %d) )\n" % \
                          (layer.name, layer.size))
            fp.writelines("net.getLayer('%s').setDisplayWidth(%d)\n" % \
                          (layer.name, layer.displayWidth))
        fp.writelines("# Connect it up:\n")
        for connect in self.connection:
            fp.writelines("net.connect( '%s', '%s')\n" % \
                          (connect.fromLayer.name, connect.toLayer.name))
        fp.writelines("# Associate it:\n")
        for assoc in self.association:
            fp.writelines("net.associate( '%s', '%s')\n" % \
                          (assoc[0], assoc[1]))
        fp.writelines("# mapInput:\n")
        for mi in self.inputMap:
            fp.writelines("net.mapInput( '%s', %d)\n" % \
                          (mi[0], mi[1]))
        fp.writelines("# mapOutput:\n")
        for mo in self.outputMap:
            fp.writelines("net.mapOutput( '%s', %d)\n" % \
                          (mo[0], mo[1]))
        fp.writelines("# Load patterns:\n")
        if len(self.output) > 0:
            fp.writelines("net.loadDataFromFile('" + basename + ".dat', %d)\n" % len(self.output[0]))
        else:
            fp.writelines("net.loadDataFromFile('" + basename + ".dat')\n")

        fp.writelines("# Load weights, biases, etc.:\n")
        fp.writelines("# net.loadWeightsFromFile('')\n")

        fp.writelines("print \"Do you want to load the weights? \",\n")
        fp.writelines("if sys.stdin.readline().lower()[0] == 'y':\n")

        mylist = self.arrayify();

        fp.writelines("\tnet.unArrayify([");
        started = 0
        for i in mylist:
            if (started):
                fp.write(", ")
            started = 1
            fp.write("%f " % i)
        fp.writelines("])\n")

        fp.writelines("print \"Do you want to re-train it? \",\n")
        fp.writelines("if sys.stdin.readline().lower()[0] == 'y':\n")
        fp.writelines("\t# Run it:\n")
        fp.writelines("\tnet.setInteractive(0)\n")
        fp.writelines("\tnet.reset()\n")
        fp.writelines("\tnet.train()\n")
        fp.writelines("print \"Do you want to see it? \",\n")
        fp.writelines("if sys.stdin.readline().lower()[0] == 'y':\n")
        fp.writelines("\t# See it:\n")
        fp.writelines("\tnet.setLearning(0)\n")
        fp.writelines("\tnet.setInteractive(1)\n")
        fp.writelines("\tnet.sweep()\n")
    def setQuickProp(self, value):
        if value:
            self.setSymmetric(1)
            self.setQp_mode(1)
            self.setEpsilon(4.0)
            self.setQp_mu(2.25)
            self.setSplit_epsilon(1)
            # FIX
            # self.setMaxrand(1.0)
        else:
            self.setSymmetric(0)
            self.setQp_mode(0)
            self.setEpsilon(0.5)
            self.setSplit_epsilon(0)
            # FIX
            # self.setMaxrand(0.4)
    def setConnectionCount(self, value):
        self.connectionCount = value
    def setPrediction(self, value):
        self.prediction = value
    def setVerbosity(self, value):
        self.verbosity = value
    def setStopPercent(self, value):
        self.stopPercent = value
    def setLayerCount(self, value):
        self.layerCount = value
    def setQp_decay(self, value):
        self.qp_decay = value
    def setQp_mode_threshold(self, value):
        self.qp_mode_threshold = value
    def setSigmoid_prime_offset(self, value):
        self.sigmoid_prime_offset = value
    def setQp_mode(self, value):
        self.qp_mode = value
    def setQp_mu(self, value):
        self.qp_mu = value
    def setSplit_epsilon(self, value):
        self.split_epsilon = value
    def setReportRate(self, value):
        self.reportRate = value
    def setSeed1(self, value):
        self.seed1 = value
    def setSeed2(self, value):
        self.seed2 = value
    def loadNetworkFromFile(self, filename):
        # just run the file
        pass
    def loadInputsFromFile(self, filename, columns = 0):
        fp = open(filename, 'r')
        line = fp.readline()
        self.input = []
        while line:
            data = map(float, line.split())
            self.input.append(data[:])
            line = fp.readline()
    def saveInputsToFile(self, filename):
        fp = open(filename, 'w')
        for i in range(len(self.input)):
            for j in range(len(self.input[i])):
                fp.write("%f " % self.input[i][j])
            fp.write("\n")
    def loadOutputsFromFile(self, filename):
        fp = open(filename, 'r')
        line = fp.readline()
        self.output = []
        while line:
            data = map(float, line.split())
            self.output.append(data[:])
            line = fp.readline()
    def saveDataToFile(self, filename):
        fp = open(filename, 'w')
        for i in range(len(self.input)):
            try:
                for j in range(len(self.input[i])):
                    fp.write("%f " % self.input[i][j])
            except:
                pass
            try:
                for j in range(len(self.output[i])):
                    fp.write("%f " % self.output[i][j])
            except:
                pass
            fp.write("\n")
    def loadDataFromFile(self, filename, ocnt = -1):
        if ocnt == -1:
            ocnt = int(self.layer[self.layerCount - 1].size)
        fp = open(filename, 'r')
        line = fp.readline()
        self.output = []
        self.input = []
        while line:
            data = map(float, line.split())
            cnt = len(data)
            icnt = cnt - ocnt
            self.input.append(data[0:icnt])
            self.output.append(data[icnt:])
            line = fp.readline()
    def saveOutputsToFile(self, filename):
        fp = open(filename, 'w')
        for i in range(len(self.output)):
            for j in range(len(self.output[i])):
                fp.write("%f " % self.output[i][j])
            fp.write("\n")

class SRN(Network):
    def addSRNLayers(self, numInput, numHidden, numOutput):
        self.add(Layer('input', numInput))
        self.add(Layer('context', numHidden))
        self.add(Layer('hidden', numHidden))
        self.add(Layer('output', numOutput))
        self.connect('input', 'hidden')
        self.connect('context', 'hidden')
        self.connect('hidden', 'output')
    def preprop(self, patnum, step):
        Network.preprop(self, patnum, step)
        if self.sequenceLength > 1 and step == 0:
            self.getLayer('context').activation = \
                Numeric.ones(self.getLayer('context').size, 'f') * .5
    def postprop(self, patnum, step):
        Network.postprop(self, patnum, step)
        self.getLayer('context').copyActivations(self.getLayer('hidden').activation)

if __name__ == '__main__':
    # Con-x: Sample XOR Network
    # (c) 2001, D.S. Blank
    # Bryn Mawr College
    # http://emergent.brynmawr.edu/

    # from pyro.brain.conx import *

    n = Network()

    #n.add( Layer('input', 2) )
    #n.add( Layer('hidden', 2) )
    #n.add( Layer('output', 1) )

    #n.connect('input', 'hidden')
    #n.connect('hidden', 'output')

    n.addThreeLayers(2, 2, 1)

    n.setInputs([[0.0, 0.0],
                 [0.0, 1.0],
                 [1.0, 0.0],
                 [1.0, 1.0]])

    n.setOutputs([[0.0],
                  [1.0],
                  [1.0],
                  [0.0]])

    n.setReportRate(100)

    # Run the network till it learns all patterns:
    print "Do you want to run an XOR BACKPROP network in BATCH mode? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print "Backprop: ............................................."
        n.setBatch(1)
        n.reset()
        n.setQuickProp(0)
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()

    print "Do you want to run an XOR BACKPROP network in NON-BATCH mode? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print "Backprop: ............................................."
        n.setBatch(0)
        n.initialize()
        n.setQuickProp(0)
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()

    print "Do you want to run an XOR QUICKPROP network? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print "Quickprop: ............................................"
        n.reset()
        n.setBatch(1)
        n.setQuickProp(1)
        n.train()

    print "Do you want to train a sequential XOR SRN? ",
    if sys.stdin.readline().lower()[0] == 'y':
        n = SRN()
        # Sequence is automatically used when the input pattern is
        # larger than the input layer: 1 input, but input pattern has
        # two elements
        n.add( Layer('input', 1) )
        n.add( Layer('context', 4) )
        n.add( Layer('hidden', 4) )
        n.add( Layer('output', 1) )

        n.connect('input', 'hidden')
        n.connect('context', 'hidden')
        n.connect('hidden', 'output')

        n.setInputs([[0.0, 0.0],
                     [0.0, 1.0],
                     [1.0, 0.0],
                     [1.0, 1.0]])

        n.setOutputs([[0.0],
                      [1.0],
                      [1.0],
                      [0.0]])

        n.setReportRate(50)
        n.setResetEpoch(5000)
        n.reset()
        n.setQuickProp(0)
        n.setEpsilon(.1)
        n.setMomentum(.9)
        n.setInteractive(0)
        n.setBatch(1)
        n.setTolerance(.3)

        n.train()
        n.setInteractive(1)
        n.sweep()

    print "Do you want to see (and save) the final network? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print "Filename to save network (.py): ",
        filename = sys.stdin.readline().strip()
        n.saveNetworkToFile(filename)
        n.setLearning(0)
        n.setInteractive(1)
        n.sweep()


