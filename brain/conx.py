""" ----------------------------------------------------
    An Artificial Neural Network System Implementing
    Backprop. Part of the Pyro Robotics Project.
    Provided under the GNU General Public License.
    ----------------------------------------------------
    (c) 2001-2004, Developmental Robotics Research Group
    ----------------------------------------------------
"""
import RandomArray, Numeric, math, random, time, sys, signal

version = "6.9"

# better to use Numeric.add.reduce()
def sum(a):
    """
    Sums elements in a sequence.
    """
    mysum = 0
    for n in a:
        mysum += n
    return mysum

def randomArray(size, max):
    """
    Returns an array initialized to random values between -max and max.
    """
    temp = RandomArray.random(size) * 2 * max
    return temp - max

# better to use array.tolist()
def toArray(thing):
    """
    Converts any sequence (such as a NumericArray) to a Python List.
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

def toStringArray(name, a, width = 0):
    """
    Returns an array (any sequence of floats, really) as a string.
    """
    string = name + ": "
    cnt = 0
    for i in a:
        string += "%4.2f  " % i 
        if width > 0 and (cnt + 1) % width == 0:
            string += '\n'
        cnt += 1
    return string

def writeArray(fp, a):
    """
    Writes a sequence a of floats to file pointed to by file pointer.
    """
    for i in a:
        fp.write("%f " % i)
    fp.write("\n")

class LayerError(AttributeError):
    """
    Used to indicate that a layer has some improper attribute (size,
    type, etc.).
    """
    
class NetworkError(AttributeError):
    """
    Used to indicate that a network has some improper attribute (no
    layers, no connections, etc.).
    """

class SRNError(NetworkError):
    """
    Used to indicate that SRN specific attributes are improper.
    """

class Layer:
    """
    Class which contains arrays of node elements (ie, activation,
    error, bias, etc).
    """
    # constructor
    def __init__(self, name, size):
        """
        Constructor for Layer class. A name and the number of nodes
        for the instance are passed as arguments.
        """
        if size <= 0:
            raise LayerError, ('Layer was initialized with size zero.' , size)
        self.name = name
        self.size = size
        self.displayWidth = size
        self.type = 'Undefined' # determined later by connectivity
        self.kind = 'Undefined' # mirrors self.type but will include 'Context'
        self.verbosity = 0
        self.log = 0
        self.logFile = ''
        self._logPtr = 0
        self.active = 1
        self.maxRandom = 0.1
        self.initialize(0.1)
    def initialize(self, epsilon):
        """
        Initializes important node values to zero for each node in the
        layer (target, error, activation, dbias, delta, netinput, bed).
        """
        self.randomize()
        self.target = Numeric.zeros(self.size, 'f')
        self.error = Numeric.zeros(self.size, 'f')
        self.activation = Numeric.zeros(self.size, 'f')
        self.dbias = Numeric.zeros(self.size, 'f')
        self.delta = Numeric.zeros(self.size, 'f')
        self.netinput = Numeric.zeros(self.size, 'f')
        self.bed = Numeric.zeros(self.size, 'f')
        # default epsilon value for all units
        self.epsilon = Numeric.ones(self.size, "f") * epsilon 
        self.targetSet = 0
        self.activationSet = 0
    def randomize(self):
        """
        Initialize node biases to random values in the range [-max, max].
        """
        self.bias = randomArray(self.size, self.maxRandom)

    # general methods
    def __len__(self):
        """
        Returns the number of nodes in the layer.
        """
        return self.size
    def __str__(self):
        return self.toString()

    # modify layer methods
    def setEpsilons(self, value):
        self.epsilon = Numeric.ones(self.size, "f") * value
    def getEpsilons(self):
        return self.epsilon
    def setEpsilonAt(self, value, pos):
        self.epsilon[pos] = value
    def getEpsilon(self):
        return self.epsilon
    def getEpsilonAt(self, pos):
        return self.epsilon[pos]
    def setActive(self, value):
        """
        Sets layer to active or inactive. Layers must be active to propagate activations.
        """
        self.active = value
    def getActive(self):
        """
        Used to determine if a layer is active or inactive.
        """
        return self.active
    def changeSize(self, newsize):
        """
        Changes the size of the layer. Should only be called through
        Network.changeLayerSize().
        """
        # overwrites current data
        if newsize <= 0:
            raise LayerError, ('Layer size changed to zero.', newsize)
        minSize = min(self.size, newsize)
        bias = randomArray(newsize, self.maxRandom)
        Numeric.put(bias, Numeric.arange(minSize), self.bias)
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

    # error and report methods
    def TSSError(self):
        """
        Returns Total Sum Squared Error for this layer's pattern.
        """
        return Numeric.add.reduce(self.error ** 2)
    def RMSError(self):
        """
        Returns Root Mean Squared Error for this layer's pattern.
        """
        tss = self.TSSError()
        return math.sqrt(tss / self.size)
    def getCorrect(self, tolerance):
        """
        Returns the number of nodes within tolerance of the target.
        """
        return Numeric.add.reduce(Numeric.fabs(self.target - self.activation) < tolerance)
    def getWinner(self, type = 'activation'):
        """
        Returns the winner of the type specified {'activation' or
        'target'}.
        """
        maxvalue = -10000
        maxpos = -1
        ttlvalue = 0
        if type == 'activation':
            ttlvalue = Numeric.add.reduce(self.activation)
            maxpos = Numeric.argmax(self.activation)
            maxvalue = self.activation[maxpos]
        elif type == 'target':
            # note that backprop() resets self.targetSet flag
            if self.targetSet == 0:
                raise LayerError, \
                      ('getWinner() called with \'target\' but target has not been set.', \
                       self.targetSet)
            ttlvalue = Numeric.add.reduce(self.target)
            maxpos = Numeric.argmax(self.target)
            maxvalue = self.target[maxpos]
        else:
            raise LayerError, ('getWinner() called with unknown layer attribute.', \
                               type)
        if self.size > 0:
            avgvalue = ttlvalue / float(self.size)
        else:
            raise LayerError, ('getWinner() called for layer of size zero.', \
                               self.size)
        return maxpos, maxvalue, avgvalue

    # used so pickle will work with log file pointer
    def __getstate__(self):
        odict = self.__dict__.copy() 
        del odict['_logPtr']
        return odict
    def __setstate__(self,dict):
        if dict['log']:
            self._logPtr = open(dict['logFile'], 'a') 
        else:
            self._logPtr = 0
        self.__dict__.update(dict)
        
    # log methods
    def setLog(self, fileName):
        """
        Opens a log file with name fileName.
        """
        self.log = 1
        self.logFile = fileName
        self._logPtr = open(fileName, "w")
    def logMsg(self, msg):
        """
        Logs a message.
        """
        self._logPtr.write(msg)
    def closeLog(self):
        """
        Closes the log file.
        """
        self._logPtr.close()
        self.log = 0
    def writeLog(self):
        """
        Writes to the log file.
        """
        if self.log:
            writeArray(self._logPtr, self.activation)

    # string and display methods
    def setDisplayWidth(self, val):
        """
        Sets self.displayWidth the the argument value.
        """
        self.displayWidth = val
    def toString(self):
        """
        Returns a string representation of Layer instance.
        """
        string = "Layer " + self.name + ": (Type " + self.kind + ") (Size " + str(self.size) + ")\n"
        if (self.type == 'Output'):
            string += toStringArray('Target    ', self.target, self.displayWidth)
        string += toStringArray('Activation', self.activation, self.displayWidth)
        if (self.type != 'Input' and self.verbosity > 0):
            string += toStringArray('Error     ', self.error, self.displayWidth)
        if (self.verbosity > 4 and self.type != 'Input'):
            string +=  toStringArray('bias      ', self.bias, self.displayWidth)
            string +=  toStringArray('dbias     ', self.dbias, self.displayWidth)
            string +=  toStringArray('delta     ', self.delta, self.displayWidth)
            string +=  toStringArray('netinput  ', self.netinput, self.displayWidth)
            string +=  toStringArray('bed       ', self.bed, self.displayWidth)
        return string 
    def display(self):
        """
        Displays the Layer instance to the screen.
        """
        print "============================="
        print "Display Layer '" + self.name + "' (kind " + self.kind + "):"
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

    # activation methods
    def getActivationsList(self):
        """
        Returns node activations in list form.
        """
        return self.activation.tolist()
    def getActivations(self):
        """
        Returns node activations in (Numeric) array form.
        """
        return self.activation
    def setActivations(self, value):
        """
        Sets all activations to the value of the argument. Value should be in the range [0,1].
        """
        if not self.activationSet == 0:
            raise LayerError, \
                  ('Activation flag not reset. Activations may have been set multiple times without any intervening call to propagate().', self.activationSet)
        if (value < 0 or value > 1) and self.kind == 'Input':
            print "Warning! Activations set to value outside of the interval [0, 1]. ", (self.name, value) 
        Numeric.put(self.activation, Numeric.arange(len(self.activation)), value)
        self.activationSet = 1
    def copyActivations(self, arr):
        """
        Copies activations from the argument array into
        layer activations.
        """
        array = Numeric.array(arr)
        if not len(array) == self.size:
            raise LayerError, \
                  ('Mismatched activation size and layer size in call to copyActivations()', \
                   (len(array), self.size))
        if not self.activationSet == 0:
            raise LayerError, \
                  ('Activation flag not reset before call to copyActivations()', \
                   self.activationSet) 
        if (Numeric.add.reduce(array < 0) or Numeric.add.reduce(array > 1)) and self.kind == 'Input':
            print "Warning! Activations set to value outside of the interval [0, 1]. ", (self.name, array) 
        self.activation = array
        self.activationSet = 1

    # target methods
    def getTargetsList(self):
        """
        Returns targets in list form.
        """
        return self.target.tolist()
    def getTargets(self):
        """
        Return targets in (Numeric) array form.
        """
        return self.target
    def setTargets(self, value):
        """
        Sets all targets the the value of the argument. This value must be in the range [0,1].
        """
        if not self.targetSet == 0:
            print 'Warning! Targets have already been set and no intervening backprop() was called.', \
                  (self.name, self.targetSet)
        if value > 1 or value < 0:
            raise LayerError, ('Targets for this layer are out of the interval [0,1].', (self.name, value))
        Numeric.put(self.target, Numeric.arange(len(self.target)), value)
        self.targetSet = 1
    def copyTargets(self, arr):
        """
        Copies the targets of the argument array into the self.target attribute.
        """
        array = Numeric.array(arr)
        if not len(array) == self.size:
            raise LayerError, \
                  ('Mismatched target size and layer size in call to copyTargets()', \
                   (len(array), self.size))
        if not self.targetSet == 0:
            print 'Warning! Targets have already been set and no intervening backprop() was called.', \
                  (self.name, self.targetSet)
        if Numeric.add.reduce(array < 0) or Numeric.add.reduce(array > 1):
            raise LayerError, ('Targets for this layer are out of range.', (self.name, array))
        self.target = array
        self.targetSet = 1

    # flag methods
    def resetFlags(self):
        """
        Resets self.targetSet and self.activationSet flags.
        """
        self.targetSet = 0
        self.activationSet = 0
    def resetTargetFlag(self):
        """
        Resets self.targetSet flag.
        """
        self.targetSet = 0
    def resetActivationFlag(self):
        """
        Resets self.activationSet flag.
        """
        self.activationSet = 0

class Connection:
    """
    Class which contains references to two layers (from and to) and the
    weights between them.
    """
    # constructor and initialization methods
    def __init__(self, fromLayer, toLayer):
        """
        Constructor for Connection class. Takes instances of source and
        destination layers as arguments.
        """
        self.fromLayer = fromLayer
        self.toLayer = toLayer
        self.frozen = 0
        self.initialize()
    def initialize(self):
        """
        Initializes self.dweight and self.wed to zero matrices.
        """
        self.randomize()
        self.dweight = Numeric.zeros((self.fromLayer.size, \
                                      self.toLayer.size), 'f')
        self.wed = Numeric.zeros((self.fromLayer.size, \
                                  self.toLayer.size), 'f')
    def randomize(self):
        """
        Sets weights to initial random values in the range [-max, max].
        """
        self.weight = randomArray((self.fromLayer.size, \
                                   self.toLayer.size),
                                  self.toLayer.maxRandom)

    def __str__(self):
        return self.toString()
    
    # connection modification methods
    def changeSize(self, fromLayerSize, toLayerSize):
        """
        Changes the size of the connection depending on the size
        change of either source or destination layer. Should only be
        called through Network.changeLayerSize().
        """
        if toLayerSize <= 0 or fromLayerSize <= 0:
            raise LayerError, ('changeSize() called with invalid layer size.', \
                               (fromLayerSize, toLayerSize))
        dweight = Numeric.zeros((fromLayerSize, toLayerSize), 'f')
        wed = Numeric.zeros((fromLayerSize, toLayerSize), 'f')
        weight = randomArray((fromLayerSize, toLayerSize),
                             self.toLayer.maxRandom)
        # copy from old to new, considering one is smaller
        minFromLayerSize = min( fromLayerSize, self.fromLayer.size)
        minToLayerSize = min( toLayerSize, self.toLayer.size)
        for i in range(minFromLayerSize):
            for j in range(minToLayerSize):
                wed[i][j] = self.wed[i][j]
                dweight[i][j] = self.dweight[i][j]
                weight[i][j] = self.weight[i][j]
        self.dweight = dweight
        self.wed = wed
        self.weight = weight

    # display methods
    def display(self):
        """
        Displays connection information to the screen.
        """
        if self.toLayer.verbosity > 0:
            print "wed: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'"
            for j in range(self.toLayer.size):
                print self.toLayer.name, "[", j, "]",
            print ''
            for i in range(self.fromLayer.size):
                print self.fromLayer.name, "[", i, "]", ": ",
                for j in range(self.toLayer.size):
                    print self.wed[i][j],
                print ''
            print ''
            print "dweight: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'"
            for j in range(self.toLayer.size):
                print self.toLayer.name, "[", j, "]",
            print ''
            for i in range(self.fromLayer.size):
                print self.fromLayer.name, "[", i, "]", ": ",
                for j in range(self.toLayer.size):
                    print self.dweight[i][j],
                print ''
            print ''
        print "Weights: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'"
        print "             ",
        for j in range(self.toLayer.size):
            print self.toLayer.name, "[", j, "]",
        print ''
        for i in range(self.fromLayer.size):
            print self.fromLayer.name, "[", i, "]", ": ",
            for j in range(self.toLayer.size):
                print self.weight[i][j],
            print ''
        print ''

    # string method
    def toString(self):
        """
        Connection information as a string.
        """
        string = ""
        if self.toLayer.verbosity > 0:
            string += "wed: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'\n" 
            string += "            "
            for j in range(self.toLayer.size):
                string += "        " + self.toLayer.name + "[" + str(j) + "]"
            string += '\n'
            for i in range(self.fromLayer.size):
                string += self.fromLayer.name+ "["+ str(i)+ "]"+ ": "
                for j in range(self.toLayer.size):
                    string += "              " + str(self.wed[i][j])
                string += '\n'
            string += '\n'
            string += "dweight: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'\n"
            string += "            "
            for j in range(self.toLayer.size):
                string += "        " + self.toLayer.name+ "["+ str(j)+ "]"
            string += '\n'
            for i in range(self.fromLayer.size):
                string += self.fromLayer.name+ "["+ str(i)+ "]"+ ": "
                for j in range(self.toLayer.size):
                    string +=  "              " + str(self.dweight[i][j])
                string += '\n'
            string += '\n'
        string += "Weights: from '" + self.fromLayer.name + "' to '" + self.toLayer.name +"'\n"
        string += "            "
        for j in range(self.toLayer.size):
            string += "        "  + self.toLayer.name+ "["+ str(j)+ "]"
        string += '\n'
        for i in range(self.fromLayer.size):
            string += self.fromLayer.name+ "["+ str(i)+ "]"+ ": "
            for j in range(self.toLayer.size):
                string +=  "    " + str(self.weight[i][j])
            string += '\n'
        string += '\n'
        return string
    
class Network:
    """
    Class which contains all of the parameters and methods needed to
    run a neural network.
    """
    # constructor
    def __init__(self, name = 'Backprop Network', verbosity = 0):
        """
        Constructor for the Network class. Takes optional name and verbosity arguments.
        """
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.name = name
        self.layers = []
        self.layersByName = {}
        self.connections = []
        self.inputMap = []
        self.targetMap = []
        self.association = []
        self.inputs = []
        self.targets = []
        self.orderedInputs = 0
        self.loadOrder = []
        self.learning = 1
        self.momentum = 0.9
        self.resetEpoch = 5000
        self.resetCount = 1
        self.resetLimit = 5
        self.batch = 0
        self.epoch = 0
        self.count = 0 # number of times propagate is called
        self.verbosity = verbosity
        self.stopPercent = 1.0
        self.sigmoid_prime_offset = 0.1
        self.tolerance = 0.4
        self.interactive = 0
        self.epsilon = 0.1
        self.reportRate = 25
        self.patterns = {}
        self.patterned = 0 # used for file IO with inputs and targets

    # general methods
    def path(self, startLayer, endLayer):
        """
        Used in error checking with verifyArchitecture() and in prop_from().
        """
        next = {startLayer.name : startLayer}
        visited = {}
        while next != {}:
            for item in next.items():
                # item[0] : name, item[1] : layer reference
                # add layer to visited dict and del from next 
                visited[item[0]] = item[1]
                del next[item[0]]
                for connection in self.connections:
                    if connection.fromLayer.name == item[0]:
                        if connection.toLayer.name == endLayer.name:
                            return 1 # a path!
                        elif next.has_key(connection.toLayer.name):
                            pass # already in the list to be traversed
                        elif visited.has_key(connection.toLayer.name):
                            pass # already been there
                        else:
                            # add to next
                            next[connection.toLayer.name] = connection.toLayer
        return 0 # didn't find it and ran out of places to go
    def __str__(self):
        """
        Returns string representation of network.
        """
        return self.toString()
    def __getitem__(self, name):
        """
        Returns the layer specified by name.
        """
        return self.layersByName[name]
    def __len__(self):
        """
        Returns the number of layers in the network.
        """
        return len(self.layers)
    def getLayerIndex(self, layer):
        """
        Given a reference to a layer, returns the index of that layer in self.layers.
        """              
        for i in range(len(self.layers)):
            if layer == self.layers[i]: # shallow cmp
                return i
        return -1 # not in list
    # methods for constructing and modifying a network
    def add(self, layer, verbosity = 0):
        """
        Adds a layer. Layer verbosity is optional (default 0).
        """
        layer.verbosity = verbosity
        self.layers.append(layer)
        self.layersByName[layer.name] = layer
    def connect(self, fromName, toName):
        """
        Connects two layers by instantiating an instance of Connection
        class.
        """
        fromLayer = self.getLayer(fromName)
        toLayer   = self.getLayer(toName)
        if self.getLayerIndex(fromLayer) >= self.getLayerIndex(toLayer):
            raise NetworkError, ('Layers out of order.', (fromLayer.name, toLayer.name))
        if (fromLayer.type == 'Output'):
            fromLayer.type = 'Hidden'
            if fromLayer.kind == 'Output':
                fromLayer.kind = 'Hidden'
        elif (fromLayer.type == 'Undefined'):
            fromLayer.type = 'Input'
            if fromLayer.kind == 'Undefined':
                fromLayer.kind = 'Input'
        if (toLayer.type == 'Input'):
            raise NetworkError, ('Connections out of order', (fromLayer.name, toLayer.name))
        elif (toLayer.type == 'Undefined'):
            toLayer.type = 'Output'
            if toLayer.kind == 'Undefined':
                toLayer.kind = 'Output'
        self.connections.append(Connection(fromLayer, toLayer))
    def addThreeLayers(self, inc, hidc, outc):
        """
        Creates a three layer network with 'input', 'hidden', and
        'output' layers.
        """
        self.add( Layer('input', inc) )
        self.add( Layer('hidden', hidc) )
        self.add( Layer('output', outc) )
        self.connect('input', 'hidden')
        self.connect('hidden', 'output')
    def changeLayerSize(self, layername, newsize):
        """
        Changes layer size. Newsize must be greater than zero.
        """
        # for all connection from to this layer, change matrix:
        for connection in self.connections:
            if connection.fromLayer.name == layername:
                connection.changeSize(  newsize, connection.toLayer.size )
            if connection.toLayer.name == layername:
                connection.changeSize( connection.fromLayer.size, newsize )
        # then, change the actual layer size:
        self.getLayer(layername).changeSize(newsize)
    def freeze(self, fromName, toName):
        """
        Freezes a connection between two layers. Weights for the connection will not be changed during learning.
        """
        for connection in self.connections:
            if connection.fromLayer.name == fromName and \
               connection.toLayer.name == toName:
                connection.frozen = 1
    def unFreeze(self, fromName, toName):
        """
        unFreezes a connection between two layers.Weights for the connection will be changed during learning.
        """
        for connection in self.connections:
            if connection.fromLayer.name == fromName and \
               connection.toLayer.name == toName:
                connection.frozen = 0

    # reset and intialization
    def reset(self):
        """
        Resets seed values.
        """
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))
        self.initialize()
    def initialize(self):
        """
        Initializes network by calling Connection.initialize() and
        Layer.initialize(). self.count is set to zero.
        """
        self.count = 0
        for connection in self.connections:
            connection.initialize()
        for layer in self.layers:
            layer.initialize(self.epsilon)
    def resetFlags(self):
        """
        Resets layer flags for activation and target.
        """
        for layer in self.layers:
            layer.resetFlags()

    # set and get methods for attributes
    def getLayer(self, name):
        """
        Returns the layer with the argument (string) name.
        """
        return self.layersByName[name]
    def setPatterned(self, value):
        """
        Sets the network to use patterns for inputs and targets.
        """
        self.patterned = value
    def setInteractive(self, value):
        """
        Sets interactive to value. Specifies if an interactive prompt
        should accompany sweep() or step().
        """
        self.interactive = value
    def setTolerance(self, value):
        """
        Sets tolerance to value. This specifies how close acceptable
        outputs must be to targets.
        """
        self.tolerance = value
    def setActive(self, layerName, value):
        """
        Sets a layer to active. Affects ce_init(), compute_error(),
        propagate(), change_weights(), display().
        """
        self.getLayer(layerName).setActive(value)
    def getActive(self, layerName):
        """
        Returns the value of the active flag for the layer specified
        by layerName.
        """
        return self.getLayer(layerName).getActive()
    def setLearning(self, value):
        """
        Sets learning to value. Determines if the network learns,
        ie. changes connection weights.
        """
        self.learning = value
    def setMomentum(self, value):
        """
        Sets self.momentum to value. Used in change_weights().
        """
        self.momentum = value
    def setResetLimit(self, value):
        """
        Sets self.resetLimit to value. When the number of resets
        reaches the reset limit the network quits.
        """
        self.resetLimit = value
    def setResetEpoch(self, value):
        """
        Sets self.resetEpoch to value. When the number of epochs
        reaches self.resetEpoch the network restarts.
        """
        self.resetEpoch = value
    def setBatch(self, value):
        """
        Sets self.batch to value. Accumulates error over the entire
        training set and only changes weights after each training
        batch is complete.
        """
        self.batch = value
    def setSeed(self, value):
        """
        Sets the seed to value.
        """
        self.seed1 = value
        self.seed2 = value / 23.45
        if int(self.seed2) <= 0:
            self.seed2 = 515
            print "Warning: random seed too small"
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))
    def getConnection(self, lfrom, lto):
        """
        Returns the connection instance connecting the specified (string) layer names.
        """
        for connection in self.connections:
            if connection.fromLayer.name == lfrom and \
               connection.toLayer.name == lto:
                return connection
        raise NetworkError, ('Connection was not found.', (lfrom, lto))
    def setVerbosity(self, value):
        """
        Sets self.verbosity and each layer verbosity to value.
        """
        self.verbosity = value
        for layer in self.layers:
            layer.verbosity = value
    def setStopPercent(self, value):
        """
        Sets self.stopPercent to value. train() will stop if the percent correct surpasses the stop percent.
        """
        self.stopPercent = value
    def setSigmoid_prime_offset(self, value):
        """
        Sets self.sigmoid_prime_offset to value.
        """
        self.sigmoid_prime_offset = value
    def setReportRate(self, value):
        """
        Sets self.reportRate to value. train() will report when epoch % reportRate == 0.
        """
        self.reportRate = value
    def setSeed1(self, value):
        """
        Sets seed1 to value. Does not initialize the random number generator.
        """
        self.seed1 = value
    def setSeed2(self, value):
        """
        Sets seed2 to value. Does not initialize the random number generator.
        """
        self.seed2 = value
    def setMaxRandom(self, value):
        """
        Sets the maxRandom Layer attribute for each layer to value.Specifies the global range for randomly initialized values, [-max, max].
        """
        for layer in self.layers:
            layer.maxRandom = value
    def getEpsilon(self):
        """
        Returns the epsilon for the Network instance.
        """
        return self.epsilon
    def setEpsilon(self, value):
        """
        Sets epsilon value for the network.
        """
        self.epsilon = value
        for layer in self.layers:
            layer.setEpsilons(value)
    def getWeights(self, fromName, toName):
        """
        Gets the weights of the connection between two layers (argument strings).
        """
        for connection in self.connections:
            if connection.fromLayer.name == fromName and \
               connection.toLayer.name == toName:
                return connection.weight
        raise NetworkError, ('Connection was not found.', (fromName, toName))
    def setOrderedInputs(self, value):
        """
        Sets self.orderedInputs to value. Specifies if inputs
        should be ordered and if so orders the inputs.
        """
        self.orderedInputs = value
        if self.orderedInputs:
            self.loadOrder = range(len(self.inputs))
    def verifyArguments(self, arg):
        """
        Verifies that arguments to setInputs and setTargets are appropriately formatted.
        """
        for l in arg:
            if not type(l) == list and \
               not type(l) == type( RandomArray.random(1) ) and \
               not type(l) == tuple:
                return 0
            for i in l:
                if not type(i) == float and not type(i) == int:
                    return 0
        return 1
    def setInputs(self, inputs):
        """
        Sets self.input to inputs. Load order is by default random. Use setOrderedInputs() to order inputs.
        """
        if not self.verifyArguments(inputs) and not self.patterned:
            raise NetworkError, ('setInputs() requires a nested list of the form [[...],[...],...].', inputs)
        self.inputs = inputs
        self.loadOrder = range(len(self.inputs)) # not random
        # will randomize later, if need be
    def setOutputs(self, outputs):
        """
        For compatiblity.
        """
        self.setTargets(outputs)
    def setTargets(self, targets):
        """
        Sets the targets.
        """
        if not self.verifyArguments(targets) and not self.patterned:
            raise NetworkError, ('setOutputs() requires a nested list of the form [[...],[...],...].', targets)
        self.targets = targets
    def associate(self, inName, outName):
        """
        inName layer and outName layer will be auto-associating.
        """
        self.association.append((inName, outName))
    def mapInput(self, vector1, offset = 0):
        """
        Adds vector and offset to inputMap.
        """
        self.inputMap.append((vector1, offset))
    def mapTarget(self, vector1, offset = 0):
        """
        Adds vector and offset to targetMap.
        """
        self.targetMap.append((vector1, offset))

    # input and target methods
    def randomizeOrder(self):
        """
        Randomizes self.loadOrder, the order in which inputs set with
        self.setInputs() are presented.
        """
        flag = [0] * len(self.inputs)
        self.loadOrder = [0] * len(self.inputs)
        for i in range(len(self.inputs)):
            pos = int(random.random() * len(self.inputs))
            while (flag[pos] == 1):
                pos = int(random.random() * len(self.inputs))
            flag[pos] = 1
            self.loadOrder[pos] = i   
    def copyVector(self, vector1, vec2, start):
        """
        Copies vec2 into vector1 being sure to replace patterns if
        necessary. Use self.copyActivations() or self.copyTargets()
        instead.
        """
        vector2 = self.replacePatterns(vec2)
        length = min(len(vector1), len(vector2))
        if self.verbosity > 1:
            print "Copying Vector: ", vector2[start:start+length]
        p = 0
        for i in range(start, start + length):
            vector1[p] = vector2[i]
            p += 1
    def copyActivations(self, layer, vec, start = 0):
        """
        Copies activations in vec to the specified layer, replacing
        patterns if necessary.
        """
        vector = self.replacePatterns(vec)
        if self.verbosity > 1:
            print "Copying Activations: ", vector[start:start+layer.size]
        layer.copyActivations(vector[start:start+layer.size])
    def copyTargets(self, layer, vec, start = 0):
        """
        Copies targets in vec to specified layer, replacing patterns
        if necessary.
        """
        vector = self.replacePatterns(vec)
        if self.verbosity > 1:
            print "Copying Target: ", vector[start:start+layer.size]
        layer.copyTargets(vector[start:start+layer.size])
    def loadInput(self, pos, start = 0):
        """
        Loads input at pos. Used with self.setInputs().
        """
        if pos >= len(self.inputs):
            raise IndexError, ('loadInput() pattern beyond range.', pos)
        if self.verbosity > 0: print "Loading input", pos, "..."
        if len(self.inputMap) == 0:
            self.copyActivations(self.layers[0], self.inputs[pos], start)
        else: # mapInput set manually
            for vals in self.inputMap:
                (v1, offset) = vals
                self.copyActivations(self.getLayer(v1), self.inputs[pos], offset)
    def loadTarget(self, pos, start = 0):
        """
        Loads target at pos. Used with self.setTargets().
        """
        if pos >= len(self.targets):
            return  # there may be no target 
        if self.verbosity > 1: print "Loading target", pos, "..."
        if len(self.targetMap) == 0:
            self.copyTargets(self.layers[len(self.layers)-1], self.targets[pos], start)
        else: # set manually
            for vals in self.targetMap:
                (v1, offset) = vals
                self.copyTargets(self.getLayer(v1), self.targets[pos], offset)

    # input, architecture, and target verification
    def verifyArchitecture(self):
        """
        Check for orphaned layers or connections. Assure that network
        architecture is feed-forward (no-cycles). Check connectivity. Check naming.
        """
        # flags for layer type tests
        hiddenInput = 1
        hiddenOutput = 1       
        outputLayerFlag = 1  
        inputLayerFlag = 1
        # must have layers and connections
        if len(self.layers) == 0:
            raise NetworkError, ('No network layers.', \
                                 self.layers)
        if len(self.connections) == 0:
            raise NetworkError, ('No network connections.', \
                                 self.connections)
        # layers should not have the same name
        for x, y in [(x, y) for x in range(len(self.layers)) for y in range(len(self.layers))]:
            if x == y:
                pass # same layer so same name
            else:
                # different layers same name
                if self.layers[x].name == self.layers[y].name:
                    raise NetworkError, ('Two layers have the same name.', (x,y))
        # no multiple connections between layers
        for x, y in [(x,y) for x in range(len(self.connections)) for y in range(len(self.connections))]:
            if x == y:
                pass # same connection
            else:
                # multiple connections between fromLayer and toLayer
                if self.connections[x].fromLayer.name == self.connections[y].fromLayer.name and \
                   self.connections[x].toLayer.name == self.connections[y].toLayer.name:
                    raise NetworkError, ('Multiple connections between two layers.', \
                                         (self.connections[x].fromLayer.name, \
                                          self.connections[x].toLayer.name))
        # layer type tests
        for layer in self.layers:
            # no undefined layers
            if layer.type == 'Undefined':
                raise NetworkError, ('There is an unconnected layer.', layer.name)
            elif layer.type == 'Input':
                for connection in self.connections:
                    # input layers must have outgoing connections 
                    if connection.fromLayer.name == layer.name:
                        inputLayerFlag = 0
                    # input layers must have no incoming connections
                    if connection.toLayer.name == layer.name:
                        raise NetworkError, \
                              ('Layer has type \'Input\' and an incoming connection.', layer.name)
                if inputLayerFlag:
                    raise NetworkError, \
                          ('Layer has type \'Input\' but no outgoing connections', layer.name)
            elif layer.type == 'Output':
                for connection in self.connections:
                    # output layers must have no outgoing connections`
                    if connection.fromLayer.name == layer.name:
                        raise NetworkError, \
                              ('Layer has type \'Output\' and an outgoing connections.',layer.name)
                    # output layers must have an incoming connection
                    if connection.toLayer.name == layer.name:
                        outputLayerFlag = 0
                if outputLayerFlag:
                    raise NetworkError, \
                          ('Layer has type \'Output\' and no incoming connections.', layer.name)           
            elif layer.type == 'Hidden':
                for connection in self.connections:
                    # hidden layers must have incoming and outgoing connections.
                    if connection.toLayer.name == layer.name:
                        hiddenInput = 0
                    if connection.fromLayer.name == layer.name:
                        hiddenOutput = 0
                if hiddenInput or hiddenOutput:
                    raise NetworkError, \
                          ('Layer has type \'Hidden\' but does not have both input and output connections.',\
                           layer.name)
            else:
                raise LayerError, ('Unknown layer encountered in verifyArchitecture().', layer.name)
        # network should not have unconnected sub networks
        # every input layer should have a path to every output layer
        for inLayer in self.layers:
            if inLayer.type == 'Input':
                for outLayer in self.layers:
                    if outLayer.type == 'Output':
                        if not self.path(inLayer, outLayer):
                            raise NetworkError, ('Network contains disconnected sub networks.', \
                                                 (inLayer.name, outLayer.name))
        # network should not have directed cycles
        for layer in self.layers:
            if self.path(layer, layer):
                raise NetworkError, ('Network contains a cycle.', layer.name)   
    def verifyInputs(self):
        """
        Used in propagate() to verify that the network input
        activations have been set.
        """
        for layer in self.layers:
            if layer.type == 'Input' and not layer.activationSet:
                raise LayerError, ('Inputs are not set and verifyInputs() was called.',\
                                   (layer.name, layer.type))
            else:
                layer.resetActivationFlag()
    def verifyTargets(self):
        """
        Used in backprop() to verify that the network targets have
        been set.
        """
        for layer in self.layers:
            if layer.type == 'Output' and not layer.targetSet:
                raise LayerError, ('Targets are not set and verifyTargets() was called.',\
                                   (layer.name, layer.type))
            else:
                layer.resetTargetFlag()

    # error reporting methods
    def getCorrect(self, layerName):
        """
        Returns the number of correct activation within tolerance of a
        layer.
        """
        return self.getLayer(layerName).getCorrect(self.tolerance)
    def RMSError(self):
        """
        Returns Root Mean Squared Error for all output layers in this network.
        """
        tss = 0.0
        size = 0
        for layer in self.layers:
            if layer.type == 'Output':
                tss += layer.TSSError()
                size += layer.size
        return math.sqrt( tss / size )
    def TSSError(self, layerName):
        """
        Returns Total Sum Squared error for the specified layer's pattern.
        """
        return self.getLayer(layerName).TSSError()

    # train and sweep methods
    def train(self):
        """
        Trains the network on the dataset till a stopping condition is
        met. This stopping condition can be a limiting epoch or a percentage correct requirement.
        """

        # check architecture
        self.verifyArchitecture()
        tssErr = 0.0; rmsErr = 0.0; self.epoch = 1; totalCorrect = 0; totalCount = 1;
        self.resetCount = 1
        while totalCount != 0 and \
              totalCorrect * 1.0 / totalCount < self.stopPercent:
            (tssErr, totalCorrect, totalCount) = self.sweep()
            rmsErr = math.sqrt(tssErr / totalCount)
            if self.epoch % self.reportRate == 0:
                print "Epoch #%6d" % self.epoch, "| TSS Error: %f" % tssErr, \
                      "| Correct =", totalCorrect * 1.0 / totalCount, \
                      "| RMS Error: %f" % rmsErr
            if self.resetEpoch == self.epoch:
                if self.resetCount == self.resetLimit:
                    print "Reset limit reached; ending without reaching goal"
                    break
                self.resetCount += 1
                print "RESET! resetEpoch reached; starting over..."
                self.initialize()
                tssErr = 0.0; rmsErr = 0.0; self.epoch = 1; totalCorrect = 0
                continue
            sys.stdout.flush()
            self.epoch += 1
        print "----------------------------------------------------"
        if totalCount > 0:
            print "Final #%6d" % self.epoch, "| TSS Error: %f" % tssErr, \
                  "| Correct =", totalCorrect * 1.0 / totalCount, \
                  "| RMS Error: %.2f" % rmsErr
        else:
            print "Final: nothing done"
        print "----------------------------------------------------"
    def sweep(self):
        """
        Runs through entire dataset. Must call setInputs(),
        setTargets(), and associate() methods to initialize all inputs
        and targets for the entire dataset before calling
        propagate() and backprop() (possibly without learning). Returns TSS error,
        total correct, and total count.
        """
        if self.loadOrder == []:
            raise NetworkError, ('No loadOrder for the inputs. Make sure inputs \
            are properly set.', self.loadOrder)
        if self.verbosity > 0: print "Epoch #", self.epoch, "Cycle..."
        if not self.orderedInputs:
            self.randomizeOrder()
        tssError = 0.0; totalCorrect = 0; totalCount = 0;
#        print 'performing sweep...'
        for i in self.loadOrder:
            if self.verbosity > 0 or self.interactive:
                print "-----------------------------------Pattern #", i + 1
            self.preprop(i)
            self.propagate()
            (error, correct, total) = self.backprop() # compute_error()
##            print '   pattern', i, ':', self.getLayer('input').activation
##            print '   pattern', i, 'targets =', self.getLayer('output').target
##            print '   pattern', i, 'outputs =', self.getLayer('output').activation
##            print '   pattern', i, 'errors =', self.getLayer('output').error
##            print '   pattern', i, 'deltas =', self.getLayer('output').delta
##            print '   sum squared error for pattern', i, '=', error
            tssError += error
            totalCorrect += correct
            totalCount += total
            if self.verbosity > 0 or self.interactive:
                self.display()
            if self.interactive:
                self.prompt()
            # the following could be in this loop, or not
            self.postprop(i)
            sys.stdout.flush()
            if self.learning and not self.batch:
                self.change_weights()
        if self.learning and self.batch:
            self.change_weights() # batch
##        print 'tssError =', tssError
##        print '   TOTAL SUM SQUARED ERROR =', tssError
##        print self.connections[1]
##        print self.connections[0]
##        self.prompt()
        return (tssError, totalCorrect, totalCount)
    def cycle(self):
        """
        Alternate to sweep().
        """
        return self.sweep()

    # pre and post prop methods for sweep
    def preprop(self, pattern, step = 0):
        """
        Used to initialize the network before
        propagation. Specifically, preprop() loads input activations
        and target values for pattern and step respectively. Likewise,
        preprop() loads target values. Preprop also initializes
        auto-association.
        """
        self.loadInput(pattern, step*self.layers[0].size)
        self.loadTarget(pattern, step*self.layers[len(self.layers)-1].size)
        for aa in self.association:
            (inName, outName) = aa
            inLayer = self.getLayer(inName)
            if not inLayer.type == 'Input':
                raise LayerError, ('Associated input layer not type \'Input\'.', \
                                   inLayer.type)
            outLayer = self.getLayer(outName)
            if not outLayer.type == 'Output':
                raise LayerError, ('Associated output layer not type \'Output\'.', \
                                   outLayer.type)
            outLayer.copyTargets(inLayer.activation)
    def postprop(self, pattern, sequence = 0):
        """
        Any necessary post propagation changes go here.
        """
        pass

    # step method 
    def step(self, **args):
        """
        Does a single step. Calls propagate(), backprop(), and
        change_weights() if learning is set. Use
        self.copyActivations() to set inputs and self.copyTargets() to
        set targets according to values passed to step via
        **args. Must pass associated targets manually. Format for parameters:
        <layer name> = <activation/target list>
        
        """
        for item in args.items():
            layer = self.getLayer(item[0])
            if layer.type == 'Input':
                layer.copyActivations(item[1])
            elif layer.type == 'Output':
                layer.copyTargets(item[1])
            else:
                raise LayerError,  ('Unkown or incorrect layer type in step() method.', layer.name)
        self.propagate()
        (error, correct, total) = self.backprop() # compute_error()
        if self.verbosity > 0 or self.interactive:
            self.display()
            if self.interactive:
                self.prompt()
        if self.learning:
            self.change_weights()
        return (error, correct, total)

    # propagation methods
    def prop_from(self, startLayers):
        """
        Start propagation from the layers in the list
        startLayers. Make sure startLayers are initialized with the
        desired activations. NO ERROR CHECKING.
        """
        if self.verbosity > 2: print "Partially propagating network:"
        # find all the layers involved in the propagation
        propagateLayers = []
        # propagateLayers should not include startLayers (no loops)
        for startLayer in startLayers:
            for layer in self.layers:
                if self.path(startLayer, layer):
                    propagateLayers.append(layer)
        for layer in propagateLayers:
            if layer.active: 
                layer.netinput = layer.bias[:]
        for layer in propagateLayers:
            if layer.active:
                for connection in self.connections:
                    if connection.toLayer.name == layer.name:
                        connection.toLayer.netinput = connection.toLayer.netinput + \
                                                      Numeric.matrixmultiply(connection.fromLayer.activation,\
                                                                             connection.weight) # propagate!
                layer.activation = self.activationFunction(layer.netinput)
        for layer in propagateLayers:
            if layer.log and layer.active:
                layer.writeLog()
    def propagate(self):
        """
        Propagates activation through the network.
        """
        self.verifyInputs() # better have inputs set
        if self.verbosity > 2: print "Propagate Network '" + self.name + "':"
        # initialize netinput:
        for layer in self.layers:
            if layer.type != 'Input' and layer.active:
                layer.netinput = layer.bias[:]
        # for each connection, in order:
        for layer in self.layers:
            if layer.active:
                for connection in self.connections:
                    if connection.toLayer.name == layer.name:
                        connection.toLayer.netinput = connection.toLayer.netinput + \
                                                      Numeric.matrixmultiply(connection.fromLayer.activation,\
                                                                             connection.weight) # propagate!
                if layer.type != 'Input':
                    layer.activation = self.activationFunction(layer.netinput)
        for layer in self.layers:
            if layer.log and layer.active:
                layer.writeLog()
        self.count += 1 # counts number of times propagate() is called
    def activationFunction(self, x):
        """
        Determine the activation of a node based on that nodes net input.
        """
        return (1.0 / (1.0 + Numeric.exp(-Numeric.maximum(Numeric.minimum(x, 15), -15))))
        
    # backpropagation
    def backprop(self):
        """
        Computes error and wed for back propagation of error.
        """
        self.verifyTargets() # better have targets set
        retval = self.compute_error()
        if self.learning:
            self.compute_wed()
        return retval
    def change_weights(self):
        """
        Changes the weights according to the error values calculated
        during backprop(). Learning must be set.
        """
        for connection in self.connections:
            if not connection.frozen:
                if connection.fromLayer.active:
                    toLayer = connection.toLayer
                    connection.dweight = toLayer.epsilon * connection.wed + self.momentum * connection.dweight
                    connection.weight = connection.weight + connection.dweight
                    connection.wed = connection.wed * 0.0
                    toLayer.dbias = toLayer.epsilon * toLayer.bed + \
                                    self.momentum * toLayer.dbias
                    toLayer.bias = toLayer.bias + toLayer.dbias
                    toLayer.bed = toLayer.bed * 0.0
        if self.verbosity > 0:
            print "WEIGHTS CHANGED"
            self.display()
    def ce_init(self):
        """
        Initializes error computation. Calculates error for output
        layers and initializes hidden layer error to zero.
        """
        retval = 0.0; correct = 0; totalCount = 0
        for layer in self.layers:
            if layer.active:
                if layer.type == 'Output':
                    layer.error = layer.target - layer.activation
                    totalCount += layer.size
                    retval += Numeric.add.reduce(layer.error ** 2)
                    correct += Numeric.add.reduce(Numeric.fabs(layer.error) < self.tolerance)
                elif (layer.type == 'Hidden'):
                    for i in range(layer.size):
                        layer.error[i] = 0.0
        return (retval, correct, totalCount)
    def compute_error(self):
        """
        Computes error for all non-output layers backwards through all
        projections.
        """
        error, correct, total = self.ce_init()
        # go backwards through each proj but don't redo output errors!
        for c in range(len(self.connections) - 1, -1, -1):
            connect = self.connections[c]
            if connect.toLayer.active:
                connect.toLayer.delta = connect.toLayer.error * self.ACTPRIME(connect.toLayer.activation)
                connect.fromLayer.error = connect.fromLayer.error + \
                                          Numeric.matrixmultiply(connect.weight,connect.toLayer.delta)
        return (error, correct, total)
    def compute_wed(self):
        """
        Computes weight error derivative for all connections in
        self.connections starting with the last connection.
        """
        for c in range(len(self.connections) - 1, -1, -1):
            connect = self.connections[c]
            connect.wed = connect.wed + Numeric.outerproduct(connect.fromLayer.activation, connect.toLayer.delta)
            connect.toLayer.bed = connect.toLayer.bed + connect.toLayer.delta
    def ACTPRIME(self, act):
        """
        Used in compute_error.
        """
        return ((act * (1.0 - act)) + self.sigmoid_prime_offset)
    def diff(self, value):
        """
        Returns value to within 0.001. Then returns 0.0.
        """
        if math.fabs(value) < 0.001:
            return 0.0
        else:
            return value

    # display and string methods
    def toString(self):
        """
        Returns the network layers as a string.
        """
        output = ""
        for layer in self.layers:
            output += layer.toString()
        return output
    def prompt(self):
        print "--More-- [quit, go] ",
        chr = sys.stdin.readline()
        if chr[0] == 'g':
            self.interactive = 0
        elif chr[0] == 'q':
            sys.exit(1)
    def display(self):
        """
        Displays the network to the screen.
        """
        print "Display network '" + self.name + "':"
        size = range(len(self.layers))
        size.reverse()
        for i in size:
            if self.layers[i].active:
                self.layers[i].display()
                if self.patterned and self.layers[i].type != 'Hidden':
                    targetWord = self.getWord( self.layers[i].target )
                    if targetWord != '':
                        print "Target = '%s'" % targetWord
                    actWord = self.getWord( self.layers[i].activation )
                    if actWord != '' or targetWord != '':
                        print "Word   = '%s'" % actWord
                if self.verbosity > 0:
                    weights = range(len(self.connections))
                    weights.reverse()
                    for j in weights:
                        if self.connections[j].toLayer.name == self.layers[i].name:
                            self.connections[j].display()
                            
    # GA support
    def arrayify(self):
        """
        Returns an array of node bias values and connection weights
        for use in a GA.
        """
        gene = []
        for layer in self.layers:
            if layer.type != 'Input':
                for i in range(layer.size):
                    gene.append( layer.bias[i] )
        for connection in self.connections:
            for i in range(connection.fromLayer.size):
                for j in range(connection.toLayer.size):
                    gene.append( connection.weight[i][j] )
        return gene
    def unArrayify(self, gene):
        """
        Copies gene bias values and weights to network bias values and
        weights.
        """
        g = 0
        # if gene is too small an IndexError will be thrown
        for layer in self.layers:
            if layer.type != 'Input':
                for i in range(layer.size):
                    layer.bias[i] = float( gene[g])
                    g += 1
        for connection in self.connections:
            for i in range(connection.fromLayer.size):
                for j in range(connection.toLayer.size):
                    connection.weight[i][j] = gene[g]
                    g += 1
        # if gene is too long we may have a problem
        if len(gene) > g:
            raise IndexError, ('Argument to unArrayify is too long.', len(gene))

    # file IO 
    def logMsg(self, layerName, message):
        """
        Logs a message with layerName log.
        """
        # will throw an exception if setLog not called
        self.getLayer(layerName).logMsg(message)
    def logLayer(self, layerName, fileName):
        """
        Sets the layerName's log feature.
        """
        self.getLayer(layerName).setLog(fileName)
    def saveWeightsToFile(self, filename, mode = 'pickle'):
        """
        Saves weights to file in pickle, plain, or tlearn mode.
        """
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
            for layer in self.layers:
                if layer.type != 'Input':
                    fp.write("# Layer: " + layer.name + "\n")
                    for i in range(layer.size):
                        fp.write("%f " % layer.bias[i] )
                    fp.write("\n")
            fp.write("# Weights\n")
            for connection in self.connections:
                fp.write("# from " + connection.fromLayer.name + " to " +
                         connection.toLayer.name + "\n")
                for i in range(connection.fromLayer.size):
                    for j in range(connection.toLayer.size):
                        fp.write("%f " % connection.weight[i][j] )
                    fp.write("\n")
            fp.close()
        elif mode == 'tlearn':
            fp = open(filename, "w")
            fp.write("NETWORK CONFIGURED BY TLEARN\n")
            fp.write("# weights after %d sweeps\n" % self.epoch)
            fp.write("# WEIGHTS\n")
            cnt = 1
            for lto in self.layers:
                if lto.type != 'Input':
                    for j in range(lto.size):
                        fp.write("# TO NODE %d\n" % cnt)
                        fp.write("%f\n" % lto.bias[j] )
                        for lfrom in self.layers:
                            try:
                                connection = self.getConnection(lfrom.name,lto.name)
                                for i in range(connection.fromLayer.size):
                                    fp.write("%f\n" % connection.weight[i][j])
                            except NetworkError: # should return an exception here
                                for i in range(lfrom.size):
                                    fp.write("%f\n" % 0.0)
                        cnt += 1
            fp.close()            
        else:
            raise ValueError, ('Unknown mode in saveWeightsToFile().', mode)
    def loadWeightsFromFile(self, filename, mode = 'pickle'):
        """
        Loads weights from a file in pickle, plain, or tlearn mode.
        """
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
            for lto in self.layers:
                if lto.type != 'Input':
                    for j in range(lto.size):
                        fp.readline() # TO NODE %d
                        lto.bias[j] = float(fp.readline())
                        for lfrom in self.layers:
                            try:
                                connection = self.getConnection(lfrom.name, lto.name)
                                for i in range(connection.fromLayer.size):
                                    connection.weight[i][j] = float( fp.readline() )
                            except NetworkError:
                                for i in range(lfrom.size):
                                    # 0.0
                                    fp.readline()
                        cnt += 1
            fp.close()            
        else:
            raise ValueError, ('Unknown mode in loadWeightFromFile()', mode)
    def saveNetworkToFile(self, filename):
        """
        Saves network to file using pickle.
        """
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
    def loadVectorsFromFile(self, filename, cols = None, everyNrows = 1,
                            delim = ' '):
        """
        Load a set of vectors from a file. Takes a filename, list of cols
        you want (or None for all), get every everyNrows (or 1 for no
        skipping), and a delimeter.
        """
        fp = open(filename, "r")
        line = fp.readline()
        lineno = 0
        lastLength = None
        data = []
        while line:
            if lineno % everyNrows == 0:
                linedata1 = [float(x) for x in line.strip().split(delim)]
            else:
                lineno += 1
                line = fp.readline()
                continue
            if cols == None: # get em all
                newdata = linedata1
            else: # just get some cols
                newdata = []
                for i in cols:
                    newdata.append( linedata1[i] )
            if lastLength == None or len(newdata) == lastLength:
                data.append( newdata )
            else:
                raise "DataFormatError", "line = %d" % lineno
            lastLength = len(newdata)
            lineno += 1
            line = fp.readline()    
        fp.close()
        return data
    def loadInputsFromFile(self, filename, cols = None, everyNrows = 1,
                           delim = ' '):
        """
        Loads inputs from file. Patterning is lost.
        """
        self.inputs = self.loadVectorsFromFile(filename, cols, everyNrows, delim)
        self.loadOrder = range(len(self.inputs))
    def saveInputsToFile(self, filename):
        """
        Saves inputs to file.
        """
        fp = open(filename, 'w')
        for input in self.inputs:
            vec = self.replacePatterns(input)
            for item in vec:
                fp.write("%f " % item)
            fp.write("\n")
    def loadTargetsFromFile(self, filename, cols = None, everyNrows = 1,
                            delim = ' '):
        """
        Loads targets from file.
        """
        self.targets = self.loadVectorsFromFile(filename, cols, everyNrows,
                                                delim)
    def saveTargetsToFile(self, filename):
        """
        Saves targets to file.
        """
        fp = open(filename, 'w')
        for target in self.targets:
            vec = self.replacePatterns(target)
            for item in vec:
                fp.write("%f " % item)
            fp.write("\n")
    def saveDataToFile(self, filename):
        """
        Saves data (targets/inputs) to file.
        """
        fp = open(filename, 'w')
        for i in range(len(self.inputs)):
            try:
                vec = self.replacePatterns(self.inputs[i])
                for item in vec:
                    fp.write("%f " % item)
            except:
                pass
            try:
                vec = self.replacePatterns(self.targets[i])
                for item in vec:
                    fp.write("%f " % item)
            except:
                pass
            fp.write("\n")
    def loadDataFromFile(self, filename, ocnt = -1):
        """
        Loads data (targets/inputs) from file.
        """
        if ocnt == -1:
            ocnt = int(self.layers[len(self.layers) - 1].size)
        fp = open(filename, 'r')
        line = fp.readline()
        self.targets = []
        self.inputs = []
        while line:
            data = map(float, line.split())
            cnt = len(data)
            icnt = cnt - ocnt
            self.inputs.append(self.patternVector(data[0:icnt]))
            self.targets.append(self.patternVector(data[icnt:]))
            line = fp.readline()
        self.loadOrder = range(len(self.inputs))

    # patterning
    def replacePatterns(self, vector):
        """
        Replaces patterned inputs or targets with activation vectors.
        """
        if not self.patterned: return vector
        if type(vector) == str:
            return self.replacePatterns(self.patterns[vector])
        elif type(vector) != list:
            return vector
        # should be a vector if we made it here
        vec = []
        for v in vector:
            if type(v) == str:
                retval = self.replacePatterns(self.patterns[v])
                if type(retval) == list:
                    vec.extend( retval )
                else:
                    vec.append( retval )
            else:
                vec.append( v )
        return vec
    def patternVector(self, vector):
        """
        Replaces vector with patterns. Used for loading inputs or
        targets from a file and still preserving patterns.
        """
        if not self.patterned: return vector
        if type(vector) == int:
            if self.getWord(vector) != '':
                return self.getWord(vector)
            else:
                return vector
        elif type(vector) == float:
            if self.getWord(vector) != '':
                return self.getWord(vector)
            else:
                return vector
        elif type(vector) == str:
            return vector
        elif type(vector) == list:
            if self.getWord(vector) != '':
                return self.getWord(vector)
        # should be a list
        vec = []
        for v in vector:
            if self.getWord(v) != '':
                retval = self.getWord(v)
                vec.append( retval )
            else:
                retval = self.patternVector(v)
                vec.append( retval )                
        return vec
    def setPatterns(self, patterns):
        """
        Sets patterns to the dictionary argument.
        """
        self.patterns = patterns
        self.patterned = 1
    def getPattern(self, word):
        """
        Returns the pattern with key word.
        """
        if self.patterns.has_key(word):
            return self.patterns[word]
        else:
            raise ValueError, ('Unknown pattern in getPattern().', word)
    def getWord(self, pattern):
        """
        Returns the word associated with pattern.
        """
        for w in self.patterns:
            if self.compare( self.patterns[w], pattern ):
                return w
        return None
    # use addPattern and delPattern
    def setPattern(self, word, vector):
        """
        Sets a pattern with key word. Better to use addPattern() and
        delPattern().
        """
        self.patterns[word] = vector
    def addPattern(self, word, vector):
        """
        Adds a pattern with key word.
        """
        if self.patterns.has_key(word):
            raise NetworkError, \
                  ('Pattern key already in use. Call delPattern to free key.', word)
        else:
            self.patterns[word] = vector
    # will raise KeyError if word is not in dict
    def delPattern(self, word):
        """
        Delete a pattern with key word.
        """
        del self.patterns[word]
    def compare(self, v1, v2):
        """
        Compares two values. Returns 1 if all values are withing
        self.tolerance of each other.
        """
        try:
            if len(v1) != len(v2): return 0
            for x, y in zip(v1, v2):
                if abs( x - y ) > self.tolerance:
                    return 0
            return 1
        except:
            # some patterns may not be vectors
            try:
                if abs( v1 - v2 ) > self.tolerance:
                    return 0
                else:
                    return 1
            except:
                return 0

class SRN(Network):
    """
    A subclass of Network. SRN allows for simple recursive networks by
    copying hidden activations back to a context layer. This subclass
    adds support for sequencing, prediction, and context layers.
    """
    # constructor
    def __init__(self):
        """
        Constructor for SRN sub-class. Support for sequences and prediction added.
        """
        Network.__init__(self)
        self.sequenceLength = 1
        self.learnDuringSequence = 0
        self.autoSequence = 1 # auto detect length of sequence from input size
        self.prediction = []
        self.initContext = 1
        self.contextLayers = {} # records layer reference and associated hidden layer
       
    # set and get methods for attributes
    def predict(self, inName, outName):
        """
        Sets prediction between an input and output layer.
        """
        self.prediction.append((inName, outName))
    def setAutoSequence(self, value):
        """
        Automatically determines the length of a sequence. Length of
        input / Number of input nodes.
        """
        self.autoSequence = value
    def setSequenceLength(self, value):
        """
        Manually sets self.sequenceLength.
        """
        self.sequenceLength = value
    def setInitContext(self, value):
        """
        Clear context layer between sequences.
        """
        self.initContext = value
    def setLearnDuringSequence(self, value):
        """
        Set self.learnDuringSequence.
        """
        self.learnDuringSequence = value

    # methods for constructing and modifying SRN network
    def addThreeLayers(self, inc, hidc, outc):
        """
        Creates a three level network with a context layer.
        """
        self.add(Layer('input', inc))
        self.addContext(Layer('context', hidc), 'hidden')
        self.add(Layer('hidden', hidc))
        self.add(Layer('output', outc))
        self.connect('input', 'hidden')
        self.connect('context', 'hidden')
        self.connect('hidden', 'output')
    def addSRNLayers(self, inc, hidc, outc):
        """
        Wraps SRN.addThreeLayers() for compatibility.
        """
        self.addThreeLayers(inc, hidc, outc)
    def addContext(self, layer, hiddenLayerName = 'hidden', verbosity = 0):
        """
        Adds a context layer. Necessary to keep self.contextLayers dictionary up to date. 
        """
        # better not add context layer first if using sweep() without mapInput
        self.add(layer, verbosity)
        if self.contextLayers.has_key(hiddenLayerName):
            raise KeyError, ('There is already a context layer associated with this hidden layer.', \
                             hiddenLayerName)
        else:
            self.contextLayers[hiddenLayerName] = layer
            layer.kind = 'Context'

    # new methods for sweep, step, propagate
    def copyHiddenToContext(self):
        """
        Uses key to identify the hidden layer associated with each
        layer in the self.contextLayers dictionary. 
        """
        for item in self.contextLayers.items():
            if self.verbosity > 2: print 'Hidden layer: ', self.getLayer(item[0]).activation
            if self.verbosity > 2: print 'Context layer before copy: ', item[1].activation
            item[1].copyActivations(self.getLayer(item[0]).activation)
            if self.verbosity > 2: print 'Context layer after copy: ', item[1].activation
    def clearContext(self, value = .5):
        """
        Clears the context layer by setting context layer to (default) value 0.5. 
        """
        for context in self.contextLayers.values():
            context.resetFlags() # hidden activations have already been copied in
            context.setActivations(value)
    def propagate(self):
        """
        Clears context layer the first time.
        """
        if self.count == 0:
            self.clearContext()
        Network.propagate(self)
    def backprop(self):
        """
        Extends backprop() from Network to automatically deal with context layers.
        """
        retval = Network.backprop(self)
        self.copyHiddenToContext() # must go after error computation
        return retval
    def step(self, **args):
        """
        Extends network step method by automatically copying hidden
        layer activations to the context layer.
        """
        if args.has_key('clearContext'):
            if args['clearContext']:
                self.clearContext()
            del args['clearContext']
        return Network.step(self, **args)
    def preprop(self, pattern, step):
        """
        Extends preprop() by adding support for clearing context layers
        and predicting.
        """
        if self.sequenceLength > 1:
            if step == 0 and self.initContext:
                self.clearContext()
        else: # if seq length is one, you better be doing ordered
            if pattern == 0 and self.initContext:
                self.clearContext()
        Network.preprop(self, pattern, step) # must go here, consider raam example
        for p in self.prediction:
            (inName, outName) = p
            inLayer = self.getLayer(inName)
            if not inLayer.type == 'Input':
                raise LayerError, ('Prediction input layer not type \'Input\'.', inLayer.type)
            outLayer = self.getLayer(outName)
            if not outLayer.type == 'Output':
                raise LayerError, ('Prediction output layer not type \'Output\'.', outLayer.type)
            if self.sequenceLength == 1:
                position = (pattern + 1) % len(self.inputs)
                outLayer.copyTargets(self.inputs[position])
            else:
                start = ((step + 1) * inLayer.size) % len(self.replacePatterns(self.inputs[pattern]))
                self.copyTargets(outLayer, self.inputs[pattern], start)
    def postprop(self, patnum, step):
        """
        Do any necessary post propagation here.
        """
        Network.postprop(self, patnum, step)
    def sweep(self):
        """
        Enables sequencing over Network.sweep().
        """
        if self.loadOrder == []:
            raise SRNError, ('No loadOrder. Make sure inputs are properly loaded and set.', self.loadOrder)
        if self.verbosity > 0: print "Epoch #", self.epoch, "Cycle..."
        if not self.orderedInputs:
            self.randomizeOrder()
        tssError = 0.0; totalCorrect = 0; totalCount = 0;
        for i in self.loadOrder:
            if self.autoSequence:
                self.sequenceLength = len(self.replacePatterns(self.inputs[i])) / self.layers[0].size
            if self.verbosity > 0 or self.interactive:
                print "-----------------------------------Pattern #", i + 1
            if self.sequenceLength <= 0:
                raise SRNError, ('Sequence length is invalid.', self.sequenceLength)
            if self.sequenceLength == 1 and self.learnDuringSequence:
                raise SRNError, ('Learning during sequence but sequence length is one.', \
                                 (self.sequenceLength, self.learnDuringSequence))
            for s in range(self.sequenceLength):
                if self.verbosity > 0 or self.interactive:
                    print "Step #", s + 1
                self.preprop(i, s)
                self.propagate()
                if (s + 1 < self.sequenceLength and not self.learnDuringSequence):
                    # don't update error or count
                    # accumulate history without learning in context layer
                    pass
                else:
                    (error, correct, total) = self.backprop() # compute_error()
                    tssError += error
                    totalCorrect += correct
                    totalCount += total
                if self.verbosity > 0 or self.interactive:
                    print 'After propagation ...........................................'
                    self.display()
                    if self.interactive:
                        self.prompt()
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
    n.setSeed(114366.64)
    n.addThreeLayers(2, 2, 1)
    n.setInputs([[0.0, 0.0],
                 [0.0, 1.0],
                 [1.0, 0.0],
                 [1.0, 1.0]
                 ])
    n.setTargets([[0.0],
                  [1.0],
                  [1.0],
                  [0.0]
                  ])
    n.setReportRate(100)

    if ask("Do you want to test the pattern replacement utility?"):
        net = Network()
        net.addThreeLayers(3, 2, 3)
        net.setTolerance(.4)
        print "Setting patterns to one 0,0,0; two 1,1,1..."
        net.setPatterns( {"one" : [0, 0, 0], "two" :  [1, 1, 1]} )
        print net.getPattern("one")
        print net.getPattern("two")
        print "Replacing patterns..."
        print net.replacePatterns(["one", "two"])
        net.setInputs([ "one", "two" ])
        net.loadInput(0)
        net.resetFlags()
        print "one is: ",
        print net["input"].getActivations()
        net.loadInput(1)
        net.resetFlags()
        print "two is: ",
        print net["input"].getActivations()
        net.addPattern("1", 1)
        net.addPattern("0", 0)
        print "Setting patterns to 0 and 1..."
        net.setInputs([ [ "0", "1", "0" ], ["1", "1", "1"]])
        print "Testing replacePatterns and patternVector..."
        print net.replacePatterns(net.inputs[0])
        print net.patternVector(net.replacePatterns(net.inputs[0]))
        net.loadInput(0)
        net.resetFlags()
        print "0 1 0 is: ",
        print net["input"].getActivations()
        net.loadInput(1)
        print "1 1 1 is: ",
        print net["input"].getActivations()
        print "Reverse look up of .2, .3, .2 is ", net.getWord([.2, .3, .2])
        print "Reverse look up of .8, .7, .5 is ", net.getWord([.8, .7, .5])
        print "Reverse look up of .8, .9, 1 is ", net.getWord([.8, .9, 1])
        if ask("Do you want to test saving and loading of patterned inputs and targets?"):
            print net.patterns
            print net.patterned
            net.setInputs(['one','two'])
            net.setTargets([['1'],['0']])
            print "Filename to save inputs: ",
            filename = sys.stdin.readline().strip()
            print "Saving Inputs: ", net.inputs
            net.saveInputsToFile(filename)
            net.loadInputsFromFile(filename)
            print "Loading Inputs: ", net.inputs
            print "Filename to save targets: ",
            filename = sys.stdin.readline().strip()
            print "Saving Targets: ", net.targets
            net.saveTargetsToFile(filename)
            net.loadTargetsFromFile(filename)
            print "Loading Targets: ", net.targets
        if ask("Do you want to test saving and loading patterned data?"):
            print "Setting inputs and targets..."
            net.setInputs(['one','two'])
            net.setTargets([['1'],['0']])
            print "Filename to save data: ",
            filename = sys.stdin.readline().strip()
            print "Saving data: "
            print net.inputs
            print net.targets
            net.saveDataToFile(filename)
            print "Loading data: "
            net.loadDataFromFile(filename, 1)
            print net.inputs
            print net.targets
            
    if ask("Do you want to test saving and loading inputs and targets with XOR?"):
        print "Filename to save inputs: ",
        filename = sys.stdin.readline().strip()
        print "Saving Inputs: ", n.inputs
        n.saveInputsToFile(filename)
        n.loadInputsFromFile(filename)
        print "Loading Inputs: ", n.inputs
        print "Filename to save targets: ",
        filename = sys.stdin.readline().strip()
        print "Saving Targets: ", n.targets
        n.saveTargetsToFile(filename)
        n.loadTargetsFromFile(filename)
        print "Loading Targets: ", n.targets

    if ask("Do you want to test saving and loading XOR data?"):
        print "Filename to save data: ",
        filename = sys.stdin.readline().strip()
        print "Saving data: "
        print n.inputs
        print n.targets
        n.saveDataToFile(filename)
        print "Loading data: "
        n.loadDataFromFile(filename, 1)
        print n.inputs
        print n.targets
        
    if ask("Do you want to see some test values?"):
        print 'Input Activations:', n.getLayer('input').getActivations()
        print "Setting target to .5"
        n.getLayer("output").copyTargets([.5])
        print 'Output Targets:', n.getLayer('output').getTargets()
        n.compute_error()
        print 'Output TSS Error:', n.TSSError("output")
        print 'Output Correct:', n.getCorrect('output')

    if ask("Do you want to run an XOR BACKPROP network in BATCH mode?"):
        print "XOR Backprop batch mode: .............................."
        n.setBatch(1)
        n.reset()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.setReportRate(10)
        n.train()

    if ask("Do you want to run an XOR BACKPROP network in NON-BATCH mode?"):
        print "XOR Backprop non-batch mode: .........................."
        n.setBatch(0)
        n.initialize()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.setReportRate(10)
        n.train()
        if ask("Do you want to test prop_from() method?"):
            n.prop_from([n.getLayer('input')])
            print "Output activations: ", n.getLayer('output').getActivations()
            print "Hidden activations: ", n.getLayer('hidden').getActivations()
            print "Now propagating directly from hidden layer..."
            n.prop_from([n.getLayer('hidden')])
            print "Output activations (should not have changed): ",  n.getLayer('output').getActivations()
            print "Hidden activations (should not have changed): ", n.getLayer('hidden').getActivations()
            print "Now setting hidden activations..."
            n.getLayer('hidden').setActivations([0.0, 0.0])
            print "Output activations: ", n.getLayer('output').getActivations()
            print "Hidden activations: ", n.getLayer('hidden').getActivations()
            print "Now propagating directly from hidden layer..."
            n.prop_from([n.getLayer('hidden')])
            print "Output activations: ",  n.getLayer('output').getActivations()
            print "Hidden activations: ", n.getLayer('hidden').getActivations()

            
    if ask("Do you want to test an AND network?"):
        print "Creating and running and network..."
        n = Network()
        n.setSeed(114366.64)
        n.add(Layer('input',2)) 
        n.add(Layer('output',1)) 
        n.connect('input','output') 
        n.setInputs([[0.0,0.0],[0.0,1.0],[1.0,0.0],[1.0,1.0]]) 
        n.setTargets([[0.0],[0.0],[0.0],[1.0]]) 
        n.setEpsilon(0.5) 
        n.setTolerance(0.2) 
        n.setReportRate(5) 
        n.train() 
        if ask("Do you want to pickle the previous network?"):
            import pickle
            print "Pickling network..."
            print "Filename to save data (.pickle): ",
            filename = sys.stdin.readline().strip()
            print "Setting log layer..."
            n.logLayer('input', 'input.log')
            # previously did not work if layer had a file pointer
            n.saveNetworkToFile(filename)
            print "Loading file..."
            fp = open(filename + ".pickle")
            n = pickle.load(fp)
            fp.close()
            print "Sweeping..."
            n.setInteractive(1)
            n.sweep()

    if ask("Do you want to train an SRN to predict the seqences 1,2,3 and 1,3,2?"):
        print "SRN ..................................................."
        print "It is not possible to perfectly predict the sequences"
        print "1,2,3 and 1,3,2 because after a 1 either a 2 or 3 may"
        print "follow."
        n = SRN()
        n.setSeed(114366.64)
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
        #n.setInteractive(1)
        #n.verbosity = 3
        temp = time.time()
        n.train()
        timer = time.time() - temp
        print "Time...", timer
    if ask("Do you want to auto-associate on 3 bit binary patterns?"):
        print "Auto-associate .........................................."
        n = Network()
        n.setSeed(114366.64)
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
        # create network:
        raam = SRN()
        raam.setSeed(114366.64)
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
        # network learning parameters:
        raam.setLearnDuringSequence(1)
        raam.setReportRate(10)
        raam.setEpsilon(0.1)
        raam.setMomentum(0.0)
        raam.setBatch(0)
        # ending criteria:
        raam.setTolerance(0.4)
        raam.setStopPercent(1.0)
        raam.setResetEpoch(5000)
        raam.setResetLimit(0)
        # train:
        temp = time.time()
        raam.train()
        timer = time.time() - temp
        print "Time...", timer
        raam.setLearning(0)
        raam.setInteractive(1)
        if ask("Do you want to see (and save) the previous network?"):
            print "Filename to save network (.pickle): ",
            filename = sys.stdin.readline().strip()
            raam.saveNetworkToFile(filename)
            raam.sweep()
        if ask("Do you want to save weights of previous network?"):
            print "Filename to save weights (.wts): ",
            filename = sys.stdin.readline().strip() + ".wts"
            raam.saveWeightsToFile(filename)
            if ask("Do you want to try loading the weights you just saved (and sweep())?"):
                print "Loading standard style weights..."
                raam.loadWeightsFromFile(filename)
                raam.sweep()
        if ask("Do you want to save weights of previous network in plain format?"):
            print "Filename to save weights (.wts): ",
            filename = sys.stdin.readline().strip() + ".wts"
            raam.saveWeightsToFile(filename, 'plain')
            if ask("Do you want to try loading the weights you just saved (and sweep())?"):
                print"Loading plain style weights..."
                raam.loadWeightsFromFile(filename, 'plain')
                raam.sweep()
        if ask("Do you want to save weights of previous network in tlearn format?"):
            print "Filename to save weights (.wts): ",
            filename = sys.stdin.readline().strip() + ".wts"
            raam.saveWeightsToFile(filename, 'tlearn')
            if ask("Do you want to try loading the tlearn style weights you just saved (and sweep())?"):
                print "Loading tlearn style weights..."
                raam.loadWeightsFromFile(filename, 'tlearn')
                raam.sweep()
                
    if ask("Do you want to train a network to both predict and auto-associate?"):
        print "SRN and auto-associate ..................................."
        n = SRN()
        n.setSeed(114366.64)
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
        n.setOrderedInputs(1)
        temp = time.time()
        n.train()
        timer = time.time() - temp
        print "Time...", timer
        n.setLearning(0)
        n.setInteractive(1)
        if ask("Do you want to see (and save) the previous network?"):
            print "Filename to save network (.pickle): ",
            filename = sys.stdin.readline().strip()
            n.saveNetworkToFile(filename)
            n.sweep()
        if ask("Do you want to save weights of previous network?"):
            print "Filename to save weights (.wts): ",
            filename = sys.stdin.readline().strip() + ".wts"
            n.saveWeightsToFile(filename)
            if ask("Do you want to try loading the weights you just saved (and sweep())?"):
                print "Loading standard style weights..."
                n.loadWeightsFromFile(filename)
                n.sweep()
        if ask("Do you want to save weights of previous network in plain format?"):
            print "Filename to save weights (.wts): ",
            filename = sys.stdin.readline().strip() + ".wts"
            n.saveWeightsToFile(filename, 'plain')
            if ask("Do you want to try loading the weights you just saved (and sweep())?"):
                print"Loading plain style weights..."
                n.loadWeightsFromFile(filename, 'plain')
                n.sweep()
        if ask("Do you want to save weights of previous network in tlearn format?"):
            print "Filename to save weights (.wts): ",
            filename = sys.stdin.readline().strip() + ".wts"
            n.saveWeightsToFile(filename, 'tlearn')
            if ask("Do you want to try loading the tlearn style weights you just saved (and sweep())?"):
                print "Loading tlearn style weights..."
                n.loadWeightsFromFile(filename, 'tlearn')
                n.sweep()
                
    if ask("Do you want to change the size of a hidden layer in 3-3-3 network?"):
        print "Creating 3-3-3 network..."
        n = Network()
        n.addThreeLayers(3,3,3)
        n.display()
        print "New hidden layer size: ",
        size = int(sys.stdin.readline().strip())
        if not type(size) == int:
            size = 0
        print "Changing size of hidden layer..."
        try:
            # exception thrown from changeSize in Connection class
            n.changeLayerSize('hidden', size)
        except LayerError, err:
            print err
        else:
            n.display()

    if ask("Do you want to test LayerError exceptions in Layer class?"):
        print "Trying to create a layer with size zero..."
        try:
            l = Layer('broken', 0)
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to change a layer of size three to size zero with changeSize()..."
        l = Layer('broken', 3)
        try:
            l.changeSize(0)
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to call getWinner for a layer attribute that doesn't exist..."
        l = Layer('broken', 3)
        try:
            l.getWinner('someAttribute')
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        # note that backprop() resets target flag
        print "Trying to call getWinner('target') where target has not been set..."
        l = Layer('broken', 3)
        try:
            l.getWinner('target')
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to call setActivations() for a layer whose activations have already been set..."
        l = Layer('broken', 3)
        l.setActivations(.5)
        try:
            l.setActivations(.2)
        except LayerError, err:
            print err
        else:
            print "No exception caught."     
        print "Trying to call copyActivations() for a layer whose activations have already been set..."
        l = Layer('broken', 3)
        l.setActivations(.5)
        try:
            l.copyActivations([.2,.2,.2])
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to call copyActivations() with an array of incorrect size..."
        l = Layer('broken', 3)
        try:
            l.copyActivations([.2,.2])
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        l = Layer('broken', 3)
        try:
            l.copyActivations([.2,.2,.2,.2])
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to call setTargets() for a layer whose activations have already been set..."
        l = Layer('broken', 3)
        l.setTargets(.5)
        try:
            l.setTargets(.2)
        except LayerError, err:
            print err
        else:
            print "No exception caught."     
        print "Trying to call copyTargets() for a layer whose activations have already been set..."
        l = Layer('broken', 3)
        l.setTargets(.5)
        try:
            l.copyTargets([.2,.2,.2])
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to call copyTargets() with an array of incorrect size..."
        l = Layer('broken', 3)
        try:
            l.copyTargets([.2,.2])
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        l = Layer('broken', 3)
        try:
            l.copyTargets([.2,.2,.2,.2])
        except LayerError, err:
            print err
        else:
            print "No exception caught."
                                 
    if ask("Do you want to test arrayify and unArrayify?"):
        print "Creating a 3-3-3 network..."
        n = Network()
        n.addThreeLayers(3,3,3)
        print "Arrayifying network..."
        array = n.arrayify()
        displayArray('Test Array', array, 6)
        print "unArrayifying network..."
        n.unArrayify(array)
        print "Now test unArrayify() for a short gene..."
        del array[-1:]
        try:
            n.unArrayify(array)
        except IndexError, err:
            print err
        else:
            print "No exception caught."
        print "Now test unArrayigy() for long gene..."
        array.extend([0.1,0.2])
        try:
            n.unArrayify(array)
        except IndexError, err:
            print err
        else:
            print "No exception caught."

    if ask("Do you want to test loadInput exception?"):
        print "Creating a 3-3-3 network..."
        n = Network()
        n.addThreeLayers(3,3,3)
        print "Calling loadInput()..."
        try:
            n.loadInput(0)
        except IndexError, err:
            print err
        else:
            print "No exception caught."
        
    if ask("Do you want to test association and prediction exceptions?"):
        print "Creating a 3-3-3 network..."
        n = Network()
        n.addThreeLayers(3,3,3)
        n.setInputs([[1,1,1]])
        n.associate('hidden','output')
        print "Attempting to associate hidden and output layers..."
        try:
            n.preprop(0)
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        n.resetFlags()
        n.associate('input','hidden')
        print "Attempting to associate input and hidden layers..."
        try:
            n.preprop(0)
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        print "Creating SRN network..."
        n = SRN()
        n.addSRNLayers(3,3,3)
        n.setInputs([[1,1,1]])
        n.predict('hidden','output')
        print "Attempting to predict hidden and output layers..."
        try:
            n.preprop(0,0)
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        n.resetFlags()
        n.predict('input','hidden')
        print "Attempting to predict input and hidden layers..."
        try:
            n.preprop(0,0)
        except LayerError, err:
            print err
        else:
            print "No exception caught."

    if ask("Do you want to test verifyInputs and verifyTargets?"):
        print "Creating a 3-3-3 network..."
        n = Network()
        n.addThreeLayers(3,3,3)
        try:
            n.verifyInputs()
        except LayerError, err:
            print err
        else:
            print "No exception caught."
        try:
            n.verifyTargets()
        except LayerError, err:
            print err
        else:
            print "No exception caught."

    if ask("Do you want to test NetworkError exceptions?"):
        print "Creating a 3-3-3 network..."
        n = Network()
        n.addThreeLayers(3,3,3)
        print "Calling sweep() without inputs..."
        try:
            # NetworkError here indicates that no inputs have been set
            n.sweep()
        except NetworkError, err:
            print err
        else:
            print "No exception caught."
        print "Calling propagate on empty network..."
        n = Network()
        try:
            n.propagate()
        except NetworkError, err:
            print err
        else:
            print "No exception caught."
        print "Calling propagate with no connections..."
        n.add(Layer('input', 3))
        n.add(Layer('output',3))
        try:
            n.propagate()
        except NetworkError, err:
            print err
        else:
            print "No exception caught."
        print "Trying to use a nonexistant connection..."
        try:
            n.getConnection('input','output')
        except NetworkError, err:
            print err
        else:
            print "No exception caught."
        try:
            n.getWeights('input','output')
        except NetworkError, err:
            print err
        else:
            print "No exception caught."

    if ask("Do you want to test SRN exceptions?"):
        print "Creating SRN network..."
        n = SRN()
        n.addSRNLayers(3,3,3)
        n.setInputs([[1,1,1]])
        n.setLearnDuringSequence(1)
        print "Sequence length is one and learnDuringSequence is set..."
        try:
            n.sweep()
        except SRNError, err:
            print err
        else:
            print "No exception caught."
        print "Sequence length is set to -1 and sweep() is called..."
        n.setLearnDuringSequence(0)
        n.setSequenceLength(-1)
        n.setAutoSequence(0)
        try:
            n.sweep()
        except SRNError, err:
            print err
        else:
            print "No exception caught."

    if ask("Do you want to test verifyArchitecture()?"):
        print "Creating normal 3-3-3 architecture..."
        n = Network()
        n.addThreeLayers(3,3,3)
        try:
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Giving two layers the same name..."
        n.getLayer('hidden').name = 'input'
        try:
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Creating 3-3-3 architecture with context layer..."
        n = SRN()
        n.addSRNLayers(3,3,3)
        try:
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Connecting context to hidden layer again..."
        n.connect('context','hidden')
        try:
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Creating an architecture with a cycle..."
        try:
            n = Network()
            n.add(Layer('1',1))
            n.add(Layer('2',1))
            n.add(Layer('3',1))
            n.add(Layer('4',1))
            n.add(Layer('5',1))
            n.connect('1','3')
            n.connect('2','3')
            n.connect('3','4')
            n.connect('4','3') #cycle
            n.connect('4','5')
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Creating an architecture with an unconnected layer..."
        n = Network()
        n.add(Layer('1',1))
        n.add(Layer('2',1))
        n.add(Layer('3',1))
        n.connect('1','3')
        try:
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Creating an architecture with two unconnected subarchitectures..."
        n = Network()
        n.add(Layer('1',1))
        n.add(Layer('2',1))
        n.add(Layer('3',1))
        n.add(Layer('4',1))
        n.connect('1','3')
        n.connect('2','4')
        try:
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."
        print "Creating an architecture with a connection between a layer and itself."
        n = Network()
        try:
            n.add(Layer('1',1))
            n.add(Layer('2',1))
            n.connect('1','2')
            n.connect('2','2')
            n.verifyArchitecture()
        except Exception, err:
            print "Caught exception. ", err
        else:
            print "Didn't catch exception."

    if ask("Test the new step() method?"):
        print "Creating 2-2-1 network..."
        n = Network()
        n.addThreeLayers(2,2,1)
        n.setInteractive(1)
        print "Using step with arguments..."
        n.step(input = [1.0,0.0], output = [1.0])
        n.getLayer('input').copyActivations([1.0,1.0])
        n.getLayer('output').copyTargets([0.0])
        print "Using step without arguments..."
        n.step()
        print "Creating SRN Network..."
        n = SRN()
        n.addSRNLayers(3,3,3)
        n.setInteractive(1)
        print "Using step with arguments..."
        n.step(input = [1.0,0.0,0.0], output = [1.0, 0.0, 0.0], clearContext = 1)
        n.step(input = [0.0,1.0,1.0], output = [0.0, 1.0, 1.0], clearContext = 0)
        print "Using step withoutarguments..."
        n.getLayer('input').copyActivations([1.0,0.0,0.0])
        n.getLayer('output').copyTargets([1.0, 0.0, 0.0])
        n.clearContext()
        n.step() 

    if ask("Additional tests?"):
        n = Network()
        n.addThreeLayers(2,2,1)
        try:
            n.setInputs([0.0,1.0])
        except Exception, err:
            print err
        try:
            n.setInputs([[[0.0]]])
        except Exception, err:
            print err
        try:
            n.setTargets([['two']])
        except Exception, err:
            print err
        n.patterned = 1
        try:
            n.setTargets([['two']])
        except Exception, err:
            print err
        else:
            print "No exception caught."
        try:
            n = Network()
            n.add(Layer('1',2))
            n.add(Layer('2',2))
            n.add(Layer('3',1))
            n.connect('2','3')
            n.connect('1','2')
            n.verifyArchitecture()
            n.setInputs([[0.0, 0.0],
                         [0.0, 1.0],
                         [1.0, 0.0],
                         [1.0, 1.0]])
            n.setTargets([[0.0],
                          [1.0],
                          [1.0],
                          [0.0]])
            n.setReportRate(100)
            n.setBatch(0)
            n.initialize()
            n.setEpsilon(0.5)
            n.setMomentum(.975)
            n.train()
        except Exception, err:
            print err
        try:
            n = Network()
            n.add(Layer('input',2))
            n.add(Layer('output',1))
            n.add(Layer('hidden',2))
            n.connect('input','hidden')
            n.connect('hidden','output')
            n.verifyArchitecture()
            n.initialize()
            n.setEpsilon(0.5)
            n.setMomentum(.975)
            #n.setInteractive(1)
            n.mapInput('input',0)
            n.mapTarget('output',0)
            n.setInputs([[0.0, 0.0],
                         [0.0, 1.0],
                         [1.0, 0.0],
                         [1.0, 1.0]])
            n.setTargets([[0.0],
                          [1.0],
                          [1.0],
                          [0.0]])
            n.train()
        except Exception, err:
            print err
