# ----------------------------------------------------
# An Artificial Neural Network System Implementing
# Backprop
# ----------------------------------------------------
# (c) 2001-2003, Developmental Robotics Research Group
# ----------------------------------------------------

import RandomArray, Numeric, math, random, time, sys, signal

version = "6.5"

def sum(a):
    mysum = 0
    for n in a:
        mysum += n
    return mysum

def randomArray(size, max):
    """
    Returns an array initialized to random values between -max and max
    """
    temp = RandomArray.random(size) * 2 * max
    return temp - max

def toArray(thing):
    """
    Converts any sequence thing (such as a NumericArray) to a Python Array.
    """
    return [x for x in thing]

def displayArray(name, a, width = 0):
    """
    Prints an array (any sequence of floats, really) to the screen.
    """
    print name + ": ",
    cnt = 0
    for i in a:
        print "%4.2f" % i,
        if width > 0 and (cnt + 1) % width == 0:
            print ''
        cnt += 1

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
        if size <= 0:
            raise 'EmptyLayerError', size
        self.name = name
        self.size = size
        self.displayWidth = size
        self.type = 'Undefined' # determined later by connectivity
        self.verbosity = 0
        self.log = 0
        self.logFile = ''
        self._logPtr = 0
        self.bepsilon = 0.1
        self.active = 1
        self.maxRandom = 0.1
        self.initialize()
    def initialize(self):
        self.randomize()
        self.target = Numeric.zeros(self.size, 'f')
        self.error = Numeric.zeros(self.size, 'f')
        self.activation = Numeric.zeros(self.size, 'f')
        self.dbias = Numeric.zeros(self.size, 'f')
        self.delta = Numeric.zeros(self.size, 'f')
        self.netinput = Numeric.zeros(self.size, 'f')
        self.bed = Numeric.zeros(self.size, 'f')
        self.targetSet = 0
        self.activationSet = 0
    def __len__(self):
        return len(self.activation)
    def changeSize(self, newsize):
        # Overwrites current data!
        if newsize <= 0:
            raise 'EmptyLayerError', newsize
        minSize = min(self.size, newsize)
        bias = randomArray(newsize, self.maxRandom)
        for i in range(minSize):
            bias[i] = self.bias[i]
        self.bias = bias
        self.size = newsize
        self.displayWidth = newsize
        self.targetSet = 0
        self.activationSet = 0
        self.target = Numeric.zeros(self.size, 'f')
        self.error = Numeric.zeros(self.size, 'f')
        self.activation = Numeric.zeros(self.size, 'f')
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
        else:
            raise "UnknownLayerAttribute", type
        if self.size > 0:
            avgvalue = ttlvalue / float(self.size)
        else:
            raise 'EmptyLayerError', self.size
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
        self.bias = randomArray(self.size, self.maxRandom)
    def toString(self):
        return "Layer " + self.name + ": type " + self.type + " size " + str(self.size) + "\n"
    def display(self):
        print "============================="
        print "Display Layer '" + self.name + "' (type " + self.type + "):"
        if (self.type == 'Output'):
            displayArray('Target    ', self.target, self.displayWidth)
        displayArray('Activation', self.activation, self.displayWidth)
        if (self.type != 'Input' and self.verbosity > 0):
            displayArray('Error     ', self.error, self.displayWidth)
        if (self.verbosity > 4 and self.type != 'Input'):
            print "    ", ; displayArray('bias', self.bias)
            print "    ", ; displayArray('dbias', self.dbias)
            print "    ", ; displayArray('delta', self.delta)
            print "    ", ; displayArray('netinput', self.netinput)
            print "    ", ; displayArray('bed', self.bed)
    def getActivations(self):
        return toArray(self.activation)
    def setActivations(self, value):
        for i in range(self.size):
            self.activation[i] = value
        if not self.activationSet == 0:
            raise 'ActivationFlagNotResetError', self.activationSet
        else:
            self.activationSet = 1
    def copyActivations(self, arr, symmetric = 0):
        if not len(arr) == self.size:
            raise 'MismatchedActivationSizeLayerSizeError', (len(arr), self.size)
        if symmetric:
            for i in range(self.size):
                self.activation[i] = arr[i] - 0.5
        else:
            for i in range(self.size):
                self.activation[i] = arr[i]
        if not self.activationSet == 0:
            raise 'ActivationFlagNotResetError', self.activationSet
        else:
            self.activationSet = 1
    def getTarget(self):
        return toArray(self.target)
    def TSSError(self):
        return sum(map(lambda (n): n ** 2, self.error))
    def RMSError(self):
        tss = self.TSSError()
        return math.sqrt(tss / self.size)
    def getCorrect(self, tolerance):
        mysum = 0
        for i in range( self.size ):
            if abs(self.target[i] - self.activation[i]) < tolerance:
                mysum += 1
        return mysum
    def setActive(self, value):
        self.active = value
    def getActive(self):
        return self.active
    def setTarget(self, value):
        for i in range(self.size):
            self.target[i] = value
        if not self.targetSet == 0:
            raise 'TargetFlagNotResetError', self.targetSet
        else:
            self.targetSet = 1
    def copyTarget(self, arr, symmetric = 0):
        if not len(arr) == self.size:
            raise 'MismatchedTargetSizeLayerSizeError', (len(arr), self.size)
        if symmetric:
            for i in range(self.size):
                self.target[i] = arr[i] - 0.5
        else:
            for i in range(self.size):
                self.target[i] = arr[i]
        if not self.targetSet == 0:
            raise 'TargetFlagNotResetError', self.targetSet
        else:
            self.targetSet = 1
    def resetFlags(self):
        self.targetSet = 0
        self.activationSet = 0
    def resetTargetFlag(self):
        self.targetSet = 0
    def resetActivationFlag(self):
        self.activationSet = 0

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
        self.frozen = 0
        self.initialize()
    def initialize(self):
        self.randomize()
        self.dweight = Numeric.zeros((self.toLayer.size, \
                                      self.fromLayer.size), 'f')
        self.wed = Numeric.zeros((self.toLayer.size, \
                                  self.fromLayer.size), 'f')
    def changeSize(self, toLayerSize, fromLayerSize):
        if toLayerSize <= 0 or fromLayerSize <= 0:
            raise 'EmptyLayerError', (toLayerSize, fromLayerSize)        
        dweight = Numeric.zeros((toLayerSize, fromLayerSize), 'f')
        wed = Numeric.zeros((toLayerSize, fromLayerSize), 'f')
        weight = randomArray((toLayerSize, fromLayerSize),
                             self.toLayer.maxRandom)
        # copy from old to new, considering one is smaller
        minToLayerSize = min( toLayerSize, self.toLayer.size)
        minFromLayerSize = min( fromLayerSize, self.fromLayer.size)
        for i in range(minFromLayerSize):
            for j in range(minToLayerSize):
                wed[j][i] = self.wed[j][i]
                dweight[j][i] = self.dweight[j][i]
                weight[j][i] = self.weight[j][i]
        self.dweight = dweight
        self.wed = wed
        self.weight = weight
    def display(self):
        if self.toLayer.verbosity > 0:
            print "wed: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'"
            for i in range(self.toLayer.size):
                print self.toLayer.name, "[", i, "]",
            print ''
            for i in range(self.fromLayer.size):
                print self.fromLayer.name, "[", i, "]", ": ",
                for j in range(self.toLayer.size):
                    print self.wed[j][i],
                print ''
            print ''
            print "dweight: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'"
            for i in range(self.toLayer.size):
                print self.toLayer.name, "[", i, "]",
            print ''
            for i in range(self.fromLayer.size):
                print self.fromLayer.name, "[", i, "]", ": ",
                for j in range(self.toLayer.size):
                    print self.dweight[j][i],
                print ''
            print ''
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
    def setSplitEpsilon(self, value):
        self.split_epsilon = value
    def getEpsilon(self):
        if (self.split_epsilon):
            return (self.epsilon / self.fromLayer.size)
        else:
            return self.epsilon
    def randomize(self):
        self.weight = randomArray((self.toLayer.size, \
                                   self.fromLayer.size),
                                  self.toLayer.maxRandom)

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
        self.association = []
        self.input = []
        self.output = []
        self.orderedInput = 0
        self.loadOrder = []
        self.learning = 1
        self.momentum = 0.9
        self.resetEpoch = 5000
        self.resetCount = 1
        self.resetLimit = 5
        self.batch = 0
        self.epoch = 0
        self.verbosity = verbosity
        self.stopPercent = 1.0
        self.sigmoid_prime_offset = 0.1
        self.symmetric = 0
        self.tolerance = 0.4
        self.interactive = 0
        self.epsilon = 0.1
        self.reportRate = 25
        self.patterns = {}
        self.patterned = 0
        self.inputLayerCount = 0
        self.outputLayerCount = 0
        self.hiddenLayerCount = 0
    def __getitem__(self, name):
        return self.layerByName[name]
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
    def setActive(self, layerName, value):
        self.getLayer(layerName).setActive(value)
    def getActive(self, layerName):
        return self.getLayer(layerName).getActive()
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
    def reset(self):
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))
        self.initialize()
    def setSeed(self, value):
        self.seed1 = value
        self.seed2 = value / 23.45
        if int(self.seed2) <= 0:
            self.seed2 = 515
            print "Warning: random seed too small"
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
    def setMaxRandom(self, value):
        for l in range(self.layerCount):
            self.layer[l].maxRandom = value
    def setEpsilon(self, value):
        self.epsilon = value
        for l in range(self.layerCount):
            self.layer[l].bepsilon = value
        for c in range(self.connectionCount):
            self.connection[c].setEpsilon(value)
    def ce_init(self):
        retval = 0.0; correct = 0; totalCount = 0
        for x in range(self.layerCount):
            if (self.layer[x].active):
                if (self.layer[x].type == 'Output'):
                    for t in range(self.layer[x].size) :
                        self.layer[x].error[t] = self.diff(self.layer[x].target[t] - self.layer[x].activation[t])
                        if (math.fabs(self.layer[x].error[t]) < self.tolerance):
                            correct += 1
                        totalCount += 1
                        retval += (self.layer[x].error[t] ** 2)
                elif (self.layer[x].type == 'Hidden'):
                    for i in range(self.layer[x].size):
                        self.layer[x].error[i] = 0.0
        return (retval, correct, totalCount)
    def compute_error(self):
        error, correct, total = self.ce_init()
        # go backwards through each proj
        for c in range(self.connectionCount - 1, -1, -1):
            # but don't redo output errors!
            connect = self.connection[c]
            if connect.toLayer.active:
                for i in range(connect.toLayer.size):
                    connect.toLayer.delta[i] = \
                      connect.toLayer.error[i] * self.ACTPRIME(connect.toLayer.activation[i])
                    for j in range(connect.fromLayer.size):
                        connect.fromLayer.error[j] += (connect.toLayer.delta[i] * \
                                                       connect.weight[i][j])
        return (error, correct, total)
    def compute_wed(self):
        for c in range(self.connectionCount - 1, -1, -1):
            connect = self.connection[c]
            for i in range(connect.toLayer.size):
                for j in range(connect.fromLayer.size):
                    connect.wed[i][j] += (connect.toLayer.delta[i] * \
                                          connect.fromLayer.activation[j])
                connect.toLayer.bed[i] += connect.toLayer.delta[i]
    def ACTPRIME(self, act):
        if self.symmetric:
            return ((0.25 - act * act) + self.sigmoid_prime_offset)
        else:
            return ((act * (1.0 - act)) + self.sigmoid_prime_offset)
    def diff(self, value):
        if math.fabs(value) < 0.001:
            return 0.0
        else:
            return value
    def replacePatterns(self, vector):
        if not self.patterned: return vector
        if type(vector) == type("string"):
            return self.replacePatterns(self.patterns[vector])
        elif type(vector) != type([1,]):
            return vector
        # should be a vector if we made it here
        vec = []
        for v in vector:
            if type(v) == type("string"):
                retval = self.replacePatterns(self.patterns[v])
                if type(retval) == type([1,]):
                    vec.extend( retval )
                else:
                    vec.append( retval )
            else:
                vec.append( v )
        return vec
    # use copyActivations or copyTarget
    def copyVector(self, vector1, vec2, start):
        vector2 = self.replacePatterns(vec2)
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
    def copyActivations(self, layer, vec, start):
        vector = self.replacePatterns(vec)
        if self.verbosity > 1:
            print "Copying Activations: ", vector[start:start+layer.size]
        layer.copyActivations(vector[start:start+layer.size], self.symmetric)
    # CopyTargets to be parallel with CopyActivations
    def copyTargets(self, layer, vec, start):
        copyTarget(self, layer, vec, start)
    def copyTarget(self, layer, vec, start):
        vector = self.replacePatterns(vec)
        if self.verbosity > 1:
            print "Copying Target: ", vector[start:start+layer.size]
        layer.copyTarget(vector[start:start+layer.size], self.symmetric)
    def loadInput(self, pos, start = 0):
        if pos >= len(self.input):
            raise "LoadInputPatternBeyondRangeError", pos
        if self.verbosity > 0: print "Loading input", pos, "..."
        if self.inputMapCount == 0:
            self.copyActivations(self.layer[0], self.input[pos], start)
        else: # mapInput set manually
            for vals in self.inputMap:
                (v1, offset) = vals
                self.copyActivations(self.getLayer(v1), self.input[pos], offset)
    def loadTarget(self, pos, start = 0):
        if pos >= len(self.output):
            return  # there may be no target 
        if self.verbosity > 1: print "Loading target", pos, "..."
        if self.outputMapCount == 0:
            self.copyTarget(self.layer[self.layerCount-1], self.output[pos], start)
        else: # mapOutput set manually
            for vals in self.outputMap:
                (v1, offset) = vals
                self.copyTarget(self.getLayer(v1), self.output[pos], offset)
    def RMSError(self):
        tss = 0.0
        size = 0
        for l in range(self.layerCount):
            if self.layer[l].type == 'Output':
                tss += self.layer[l].TSSError()
                size += self.layer[l].size
        return math.sqrt( tss / size )
    def train(self):
        tssErr = 1.0; self.epoch = 1; totalCorrect = 0; totalCount = 1;
        self.resetCount = 1
        while totalCount != 0 and \
              totalCorrect * 1.0 / totalCount < self.stopPercent:
            (tssErr, totalCorrect, totalCount) = self.sweep()
            if self.epoch % self.reportRate == 0:
                print "Epoch #%6d" % self.epoch, "| TSS Error: %.2f" % tssErr, \
                      "| Correct =", totalCorrect * 1.0 / totalCount, \
                      "| RMS Error: %.2f" % self.RMSError()
            if self.resetEpoch == self.epoch:
                if self.resetCount == self.resetLimit:
                    print "Reset limit reached; ending without reaching goal"
                    break
                self.resetCount += 1
                print "RESET! resetEpoch reached; starting over..."
                self.initialize()
                tssErr = 1.0; self.epoch = 1; totalCorrect = 0
                continue
            sys.stdout.flush()
            self.epoch += 1
        print "----------------------------------------------------"
        if totalCount > 0:
            print "Final #%6d" % self.epoch, "| TSS Error: %.2f" % tssErr, \
                  "| Correct =", totalCorrect * 1.0 / totalCount
        else:
            print "Final: nothing done"
        print "----------------------------------------------------"
    def cycle(self):
        return self.sweep()
    def preprop(self, pattern, step = 0):
        self.loadInput(pattern, step*self.layer[0].size)
        self.loadTarget(pattern, step*self.layer[self.layerCount-1].size)
        for aa in self.association:
            (inName, outName) = aa
            inLayer = self.getLayer(inName)
            if not inLayer.type == 'Input':
                raise 'AssociateInputLayerTypeError', inLayer.type
            outLayer = self.getLayer(outName)
            if not outLayer.type == 'Output':
                raise 'AssociateOutputLayerTypeError', outLayer.type
            outLayer.copyTarget(inLayer.activation)
    def verifyInputs(self):
        for l in self.layer:
            if l.type == 'Input' and not l.activationSet:
                raise 'InputNotSetError', (l.name, l.type)
            else:
                l.resetActivationFlag()
    def verifyTargets(self):
        for l in self.layer:
            if l.type == 'Output' and not l.targetSet:
                raise 'OutputNotSetError', (l.name, l.type)
            else:
                l.resetTargetFlag()
    def resetFlags(self):
        for l in self.layer:
            l.resetFlags()
    def postprop(self, pattern, sequence = 0):
        pass
    def sweep(self):
        if self.loadOrder == []:
            raise 'LoadOrderEmptyError'
        if self.verbosity > 0: print "Epoch #", self.epoch, "Cycle..."
        if not self.orderedInput:
            self.randomizeOrder()
        tssError = 0.0; totalCorrect = 0; totalCount = 0;
        for i in self.loadOrder:
            if self.verbosity > 0 or self.interactive:
                print "-----------------------------------Pattern #", i + 1
            self.preprop(i)
            self.propagate()
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
            self.postprop(i)
            sys.stdout.flush()
            if self.learning and not self.batch:
                self.change_weights()
        if self.learning and self.batch:
            self.change_weights() # batch
        return (tssError, totalCorrect, totalCount)
    def step(self):
        self.epoch += 1
        self.propagate()
        (error, correct, total) = self.backprop() # compute_error()
        if self.verbosity > 0 or self.interactive:
            self.display()
            if self.interactive:
                print "--More-- [quit, go] ",
                chr = sys.stdin.readline()
                if chr[0] == 'g':
                    self.interactive = 0
                elif chr[0] == 'q':
                    sys.exit(1)
        if self.learning:
            self.change_weights()
        return (error, correct, total)        
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
            self.outputLayerCount -= 1
            self.hiddenLayerCount += 1
        elif (fromLayer.type == 'Undefined'):
            fromLayer.type = 'Input'
            self.inputLayerCount += 1
        if (toLayer.type == 'Input'):
            toLayer.type = 'Output'
            self.inputLayerCount -= 1
            self.outputLayerCount += 1
        elif (toLayer.type == 'Undefined'):
            toLayer.type = 'Output'
            self.outputLayerCount += 1
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
    def propagate(self):
        if self.layerCount == 0:
            raise 'NoNetworkLayersError', self.layerCount
        if self.connectionCount == 0:
            raise 'NoNetworkConnectionsError', self.connectionCount
        self.verifyInputs() # better have inputs set
        if self.verbosity > 2: print "Propagate Network '" + self.name + "':"
        # Initialize netinput:
        for n in range(self.layerCount):
            if (self.layer[n].type != 'Input' and self.layer[n].active):
                for i in range(self.layer[n].size):
                    self.layer[n].netinput[i] = self.layer[n].bias[i]
        # For each connection, in order:
        for n in range(self.layerCount):
            if self.layer[n].active:
                for c in range(self.connectionCount):
                    if (self.connection[c].toLayer.name == self.layer[n].name):
                        self.prop_process(self.connection[c]) # propagate!
                if (self.layer[n].type != 'Input'):
                    for i in range(self.layer[n].size):
                        self.layer[n].activation[i] = self.activationFunction(self.layer[n].netinput[i])
        for n in range(self.layerCount):
            if self.layer[n].log and self.layer[n].active:
                self.layer[n].writeLog()
    def prop_process(self, connect):
        if self.verbosity > 5:
            print "Prop_process from " + connect.fromLayer.name + " to " + \
                  connect.toLayer.name
        for i in range(connect.toLayer.size):
            if self.verbosity > 6: print "netinput@", connect.toLayer.name, \
               "starts at", connect.toLayer.netinput[i]
            for j in range(connect.fromLayer.size):
                if self.verbosity > 6: print "netinput@", \
                   connect.toLayer.name, "[", i, "] = ", \
                   connect.fromLayer.activation[j], "*", connect.weight[i][j]
                connect.toLayer.netinput[i] += (connect.fromLayer.activation[j] * connect.weight[i][j])
                if self.verbosity > 6: print "netinput@", \
                   connect.toLayer.name, "[", i, "] = ", \
                   connect.toLayer.netinput[i]
    def backprop(self):
        self.verifyTargets() # better have targets set
        retval = self.compute_error()
        if self.learning:
            self.compute_wed()
        return retval
    def change_weights(self):
        for c in range(self.connectionCount):
            connect = self.connection[c]
            if not connect.frozen:
                for i in range(connect.toLayer.size):
                    if connect.fromLayer.active:
                        for j in range(connect.fromLayer.size):
                            connect.dweight[i][j] = connect.getEpsilon() * connect.wed[i][j] + \
                                                    self.momentum * connect.dweight[i][j]
                            connect.weight[i][j] += connect.dweight[i][j]
                            connect.wed[i][j] = 0.0
                        toLayer = connect.toLayer
                        toLayer.dbias[i] = toLayer.bepsilon * toLayer.bed[i] + \
                                           self.momentum * toLayer.dbias[i]
                        toLayer.bias[i] += toLayer.dbias[i]
                        toLayer.bed[i] = 0.0
        if self.verbosity > 0:
            print "WEIGHTS CHANGED"
            self.display()
    def getLayer(self, name):
        return self.layerByName[name]
    def getWeights(self, fromName, toName):
        for i in range(self.connectionCount):
            if self.connection[i].fromLayer.name == fromName and \
               self.connection[i].toLayer.name == toName:
                return self.connection[i].weight
        raise 'ConnectionNotFoundError', (fromName, toName)
    def freeze(self, fromName, toName):
        for i in range(self.connectionCount):
            if self.connection[i].fromLayer.name == fromName and \
               self.connection[i].toLayer.name == toName:
                self.connection[i].frozen = 1
    def unFreeze(self, fromName, toName):
        for i in range(self.connectionCount):
            if self.connection[i].fromLayer.name == fromName and \
               self.connection[i].toLayer.name == toName:
                self.connection[i].frozen = 0
    def TSSError(self, layerName):
        return self.getLayer(layerName).TSSError()
    def getCorrect(self, layerName):
        return self.getLayer(layerName).getCorrect(self.tolerance)
    def toString(self):
        output = ""
        for i in range(self.layerCount):
            output += self.layer[i].toString()
        return output
    def display(self):
        print "Display network '" + self.name + "':"
        size = range(self.layerCount)
        size.reverse()
        for i in size:
            if self.layer[i].active:
                self.layer[i].display()
                if self.patterned and self.layer[i].type != 'Hidden':
                    targetWord = self.getWord( self.layer[i].target )
                    if targetWord != '':
                        print "Target = '%s'" % targetWord
                    actWord = self.getWord( self.layer[i].activation )
                    if actWord != '' or targetWord != '':
                        print "Word   = '%s'" % actWord
                if self.verbosity > 0:
                    weights = range(self.connectionCount)
                    weights.reverse()
                    for j in weights:
                        if self.connection[j].toLayer.name == self.layer[i].name:
                            self.connection[j].display()
    def addThreeLayers(self, inc, hidc, outc):
        self.add( Layer('input', inc) )
        self.add( Layer('hidden', hidc) )
        self.add( Layer('output', outc) )
        self.connect('input', 'hidden')
        self.connect('hidden', 'output')
    def saveWeightsToFile(self, filename, mode = 'pickle'):
        # modes: pickle, plain, tlearn
        if mode == 'pickle':
            mylist = self.arrayify()
            import pickle
            fp = open(filename, "w")
            pickle.dump(mylist, fp)
            fp.close()
        elif mode == 'plain':
            fp = open(filename, "w")
            fp.write("# Biases\n")
            for lay in self.layer:
                if lay.type != 'Input':
                    fp.write("# Layer: " + lay.name + "\n")
                    for i in range(lay.size):
                        fp.write("%f " % lay.bias[i] )
                    fp.write("\n")
            fp.write("# Weights\n")
            for con in self.connection:
                fp.write("# from " + con.fromLayer.name + " to " +
                         con.toLayer.name + "\n")
                for j in range(con.fromLayer.size):
                    for i in range(con.toLayer.size):
                        fp.write("%f " % con.weight[i][j] )
                    fp.write("\n")
            fp.close()
        elif mode == 'tlearn':
            fp = open(filename, "w")
            fp.write("NETWORK CONFIGURED BY TLEARN\n")
            fp.write("# weights after %d sweeps\n" % self.epoch)
            fp.write("# WEIGHTS\n")
            cnt = 1
            for lto in range(self.layerCount):
                if self.layer[lto].type != 'Input':
                    for i in range(self.layer[lto].size):
                        fp.write("# TO NODE %d\n" % cnt)
                        fp.write("%f\n" % self.layer[lto].bias[i] )
                        for lfrom in range(self.layerCount):
                            conn = self.getConnection(self.layer[lto].name,
                                                      self.layer[lfrom].name)
                            if conn:
                                for j in range(conn.fromLayer.size):
                                    fp.write("%f\n" % conn.weight[i][j])
                            else:
                                for j in range(self.layer[lfrom].size):
                                    fp.write("%f\n" % 0.0)
                        cnt += 1
            fp.close()            
        else:
            raise "UnknownMode", mode
    def loadWeightsFromFile(self, filename, mode = 'pickle'):
        # modes: pickle, plain, tlearn
        if mode == 'pickle':
            import pickle
            fp = open(filename, "r")
            mylist = pickle.load(fp)
            fp.close()
            self.unArrayify(mylist)
        elif mode == 'plain':
            arr = []
            fp = open(filename, "r")
            lines = fp.readlines()
            for line in lines:
                line = line.strip()
                if line == '' or line[0] == '#':
                    pass
                else:
                    data = map( float, line.split())
                    arr.extend( data )
            self.unArrayify( arr )
            fp.close()
        elif mode == 'tlearn':
            fp = open(filename, "r")
            fp.readline() # NETWORK CONFIGURED BY
            fp.readline() # # weights after %d sweeps
            fp.readline() # # WEIGHTS
            cnt = 1
            for lto in range(self.layerCount):
                if self.layer[lto].type != 'Input':
                    for i in range(self.layer[lto].size):
                        fp.readline() # TO NODE %d
                        self.layer[lto].bias[i] = float(fp.readline())
                        for lfrom in range(self.layerCount):
                            conn = self.getConnection(self.layer[lto].name,
                                                      self.layer[lfrom].name)
                            if conn:
                                for j in range(conn.fromLayer.size):
                                    conn.weight[i][j] = float( fp.readline() )
                            else:
                                for j in range(self.layer[lfrom].size):
                                    # 0.0
                                    fp.readline()
                        cnt += 1
            fp.close()            
        else:
            raise "UnknownMode", mode
    def getConnection(self, lto, lfrom):
        for c in range(self.connectionCount):
            if self.connection[c].toLayer.name == lto and \
               self.connection[c].fromLayer.name == lfrom:
                return self.connection[c]
        raise 'ConnectionNotFoundError', (lto, lfrom)
    def saveNetworkToFile(self, filename):
        import pickle
        basename = filename.split('.')[0]
        filename += ".pickle"
        fp = open(filename, 'w')
        pickle.dump( self, fp)
        fp.close()
        fp = open(basename + ".py", "w")
        fp.write("from pyro.brain.conx import *\n")
        fp.write("import pickle\n")
        fp.write("fp = open('%s', 'r')\n" % filename)
        fp.write("network = pickle.load(fp)")
        fp.close()
        print "To load file:\npython -i %s " % (basename + ".py")
        print ">>> network.train()"
    def setConnectionCount(self, value):
        self.connectionCount = value
    def setPrediction(self, value):
        self.prediction = value
    def setVerbosity(self, value):
        self.verbosity = value
        for l in range(self.layerCount):
            self.layer[l].verbosity = value
    def setStopPercent(self, value):
        self.stopPercent = value
    def setLayerCount(self, value):
        self.layerCount = value
    def setSigmoid_prime_offset(self, value):
        self.sigmoid_prime_offset = value
    def setSplit_epsilon(self, value):
        self.split_epsilon = value
    def setReportRate(self, value):
        self.reportRate = value
    def setSeed1(self, value):
        self.seed1 = value
    def setSeed2(self, value):
        self.seed2 = value
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
            vec = self.replacePatterns(self.input[i])
            for j in range(len(vec)):
                fp.write("%f " % vec[j])
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
                vec = self.replacePatterns(self.input[i])
                for j in range(len(vec)):
                    fp.write("%f " % vec[j])
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
    def changeLayerSize(self, layername, newsize):
        # for all connection from to this layer, change matrix:
        for c in range( self.connectionCount ):
            if self.connection[c].fromLayer.name == layername:
                self.connection[c].changeSize( self.connection[c].toLayer.size, newsize)
            if self.connection[c].toLayer.name == layername:
                self.connection[c].changeSize( newsize, self.connection[c].fromLayer.size)
        # Then, change the actual layer size:
        self.layerByName[layername].changeSize(newsize)
    def setPatterns(self, patterns):
        # pass in a dictionary
        self.patterns = patterns
        self.patterned = 1
    def getPattern(self, word):
        if self.patterns.has_key(word):
            return self.patterns[word]
        else:
            raise "UnknownPattern", word
    def getWord(self, pattern):
        for w in self.patterns:
            if self.compare( self.patterns[w], pattern ):
                return w
        return ""
    def setPattern(self, word, vector):
        self.patterns[word] = vector
    def compare(self, v1, v2):
        try:
            if len(v1) != len(v2): return 0
            for i in range(len(v1)):
                if abs( v1[i] - v2[i]) > self.tolerance:
                    return 0
            return 1
        except:
            return 0

class SRN(Network):
    def __init__(self):
        self.sequenceLength = 1
        self.learnDuringSequence = 0
        self.autoSequence = 1 # auto detect length of sequence from input size
        self.prediction = []
        self.initContext = 1
        Network.__init__(self)
    def setInitContext(self, value):
        self.initContext = value
    def setLearnDuringSequence(self, value):
        self.learnDuringSequence = value
    def addSRNLayers(self, numInput, numHidden, numOutput):
        self.add(Layer('input', numInput))
        self.addContext(Layer('context', numHidden))
        self.add(Layer('hidden', numHidden))
        self.add(Layer('output', numOutput))
        self.connect('input', 'hidden')
        self.connect('context', 'hidden')
        self.connect('hidden', 'output')
    def addContext(self, layer, verbosity = 0):
        # better not add context layer first
        self.add(layer, verbosity)
        self.contextLayer = layer
    def clearContext(self):
        self.contextLayer.resetFlags()
        self.contextLayer.setActivations(.5)
    def preprop(self, pattern, step):
        if self.sequenceLength > 1:
            if step == 0 and self.initContext:
                self.clearContext()
        else: # if seq length is one, you better be doing ordered
            if pattern == 0 and self.initContext:
                self.clearContext()
        Network.preprop(self, pattern, step)
        for p in self.prediction:
            (inName, outName) = p
            inLayer = self.getLayer(inName)
            if not inLayer.type == 'Input':
                raise 'PredictionInputLayerTypeError', inLayer.type
            outLayer = self.getLayer(outName)
            if not outLayer.type == 'Output':
                raise 'PredictionOutputLayerTypeError', outLayer.type
            if self.sequenceLength == 1:
                position = (pattern + 1) % len(self.input)
                outLayer.copyTarget(self.input[position])
            else:
                start = ((step + 1) * inLayer.size) % len(self.replacePatterns(self.input[pattern]))
                self.copyTarget(outLayer, self.input[pattern], start)
    def postprop(self, patnum, step):
        Network.postprop(self, patnum, step)
        self.getLayer('context').copyActivations(self.getLayer('hidden').activation)
    def sweep(self):
        if self.loadOrder == []:
            raise 'LoadOrderEmptyError'
        if self.verbosity > 0: print "Epoch #", self.epoch, "Cycle..."
        if not self.orderedInput:
            self.randomizeOrder()
        tssError = 0.0; totalCorrect = 0; totalCount = 0;
        for i in self.loadOrder:
            if self.autoSequence:
                self.sequenceLength = len(self.replacePatterns(self.input[i])) / self.layer[0].size
            if self.verbosity > 0 or self.interactive:
                print "-----------------------------------Pattern #", i + 1
            if self.sequenceLength <= 0:
                raise 'SequenceLengthError', self.sequenceLength
            if self.sequenceLength == 1 and self.learnDuringSequence:
                raise 'LearningDuringSequenceError', (self.sequenceLength, self.learnDuringSequence)
            for s in range(self.sequenceLength):
                if self.verbosity > 0 or self.interactive:
                    print "Step #", s + 1
                self.preprop(i, s)
                self.propagate()
                if (s + 1 < self.sequenceLength and not self.learnDuringSequence):
                    pass # don't update error or count - accumulate history without learning in context layer
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
                sys.stdout.flush()
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

try:
    import psyco
    psyco.bind(Layer)
    psyco.bind(Connection)
    psyco.bind(Network)
    print "Psyco is installed: running pyro.brain.conx at psyco speed..."
except:
    pass

if __name__ == '__main__':
    # Con-x: Sample Networks
    # (c) 2001, D.S. Blank
    # Bryn Mawr College
    # http://emergent.brynmawr.edu/
    def ask(question):
        print question, '[y/n/q] ',
        ans = sys.stdin.readline()[0].lower()
        if ans == 'q':
            sys.exit()
        return ans == 'y'

    n = Network()
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

    if ask("Do you want to test the pattern replacement utility?"):
        net = Network()
        net.addThreeLayers(3, 2, 3)
        print "Setting patterns to one 0,0,0; two 1,1,1..."
        net.setPatterns( {"one": [0, 0, 0], "two": [1, 1, 1]} )
        print net.getPattern("one")
        print net.getPattern("two")
        net.setInputs([ "one", "two" ])
        net.loadInput(0)
        net.resetFlags()
        print "one is: ",
        print net["input"].activation
        net.loadInput(1)
        net.resetFlags()
        print "two is: ",
        print net["input"].activation
        net.setPattern("1", 1)
        net.setPattern("0", 0)
        print "Setting patterns to 0 and 1..."
        net.setInputs([ [ "0", "1", "0" ], ["1", "1", "1"]])
        net.loadInput(0)
        net.resetFlags()
        print "0 1 0 is: ",
        print net["input"].activation
        net.loadInput(1)
        print "1 1 1 is: ",
        print net["input"].activation
        print "Reverse look up of .2, .3, .2 is ", net.getWord([.2, .3, .2])
        print "Reverse look up of .8, .7, .5 is ", net.getWord([.8, .7, .5])
        print "Reverse look up of .8, .9, 1 is ", net.getWord([.8, .9, 1])

    if ask("Do you want to see some test values?"):
        print 'Input Activations:', n.getLayer('input').getActivations()
        print "Setting output target to .5"
        n.getLayer("output").copyTarget([.5])
        print 'Output Targets:', n.getLayer('output').getTarget()
        n.compute_error()
        print 'Output TSS Error:', n.TSSError("output")
        print 'Output Correct:', n.getCorrect('output')

    if ask("Do you want to run an XOR BACKPROP network in BATCH mode?"):
        print "XOR Backprop batch mode: .............................."
        n.setBatch(1)
        n.reset()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()

    if ask("Do you want to run an XOR BACKPROP network in NON-BATCH mode?"):
        print "XOR Backprop non-batch mode: .........................."
        n.setBatch(0)
        n.initialize()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()

    if ask("Do you want to train an SRN to predict the seqences 1,2,3 and 1,3,2?"):
        print "SRN ..................................................."
        print "It is not possible to perfectly predict the sequences"
        print "1,2,3 and 1,3,2 because after a 1 either a 2 or 3 may"
        print "follow."
        n = SRN()
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
        n.train()

    if ask("Do you want to auto-associate on 3 bit binary patterns?"):
        print "Auto-associate .........................................."
        n = Network()
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
        n.train()

    if ask("Do you want to test a raam network?"):
        print "Raam ...................................................."
        # Create network:
        raam = SRN()
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
        # Network learning parameters:
        raam.setLearnDuringSequence(1)
        raam.setReportRate(10)
        raam.setEpsilon(0.1)
        raam.setMomentum(0.0)
        raam.setBatch(0)
        # Ending criteria:
        raam.setTolerance(0.4)
        raam.setStopPercent(1.0)
        raam.setResetEpoch(5000)
        raam.setResetLimit(0)
        # Train:
        raam.train()

    if ask("Do you want to see (and save) the raam network weights?"):
        print "Filename to save network (.wts): ",
        filename = sys.stdin.readline().strip() + ".wts"
        raam.saveWeightsToFile(filename)
        raam.setLearning(0)
        raam.setInteractive(1)
        raam.sweep()

    if ask("Do you want to train a network to both predict and auto-associate?"):
        print "SRN and auto-associate ..................................."
        n = SRN()
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
        n.setOrderedInput(1)
        n.train()

    if ask("Do you want to see (and save) the final network?"):
        print "Filename to save network (.pickle): ",
        filename = sys.stdin.readline().strip()
        n.saveNetworkToFile(filename)
        n.setLearning(0)
        n.setInteractive(1)
        n.sweep()

    if ask("Do you want to save weights of final network?"):
        print "Filename to save weights (.wts): ",
        filename = sys.stdin.readline().strip() + ".wts"
        n.saveWeightsToFile(filename)
