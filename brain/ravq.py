import Numeric, math

# general functions
def averageVector(V):
    """
    Determines the average vector of a set of vectors V.
    """
    return Numeric.add.reduce(V) / len(V)

def euclideanDistance(x, y):
    """
    Takes two Numeric vectors as arguments.
    """
    return math.sqrt(Numeric.add.reduce((x - y) ** 2))

def SetDistance(X, V):
    """
    Takes two lists of Numeric vectors as arguments.
    """
    min = []
    sum = 0
    for x in X:
        for v in V:
            min.append(euclideanDistance(x,v))
        sum += min[Numeric.argmin(min)]
    return sum / len(X)

def displayArray(a, width = 0):
    """
    Prints an array (any sequence of floats, really) to the screen.
    """
    cnt = 0
    for i in a:
        print "%4.4f" % i,
        if width > 0 and (cnt + 1) % width == 0:
            print ''
        cnt += 1
    print ''

def stringArray(a, width = 0):
    """
    String form of an array (any sequence of floats, really) to the screen.
    """
    s = ""
    cnt = 0
    for i in a:
        s += "%4.4f " % i
        if width > 0 and (cnt + 1) % width == 0:
            s += '\n'
        cnt += 1
    s += '\n'
    return s
    
class RAVQ:
    """
    Implements RAVQ algorithm as described in Linaker and Niklasson.
    """
    def __init__(self, size, epsilon, delta):
        self.epsilon = epsilon
        self.delta = delta
        self.size = size
        self.buffer = []
        self.models = []
        self.time = 0
        self.movingAverage = 'No Moving Average'
        self.movingAverageDistance = -1
        self.modelVectorsDistance = -1
        self.winner = 'No Winner'
        self.winnerIndex = -1
        self.verbosity = 0
        self.labels = {}
        self.recordHistory = 1
        self.history = {} # time indexed list of winners
        self.tolerance = delta

    # update the RAVQ
    def input(self, vec):
        array = Numeric.array(vec, 'd')
        if self.time < self.size:
            self.buffer.append(array)
        else:
            self.buffer = self.buffer[1:] + [array]
            self.process() # process new information
        if self.verbosity > 1: self.display()
        self.time += 1

    # attribute methods
    def setVerbosity(self, value):
        self.verbosity = value
    def setHistory(self, value):
        self.recordHistory = value
        
    # process happens once the buffer is full
    def process(self):
        self.setMovingAverage()
        self.setMovingAverageDistance()
        self.setModelVectorsDistance()
        self.updateModelVectors()
        self.updateWinner()
    def setMovingAverage(self):
        self.movingAverage = averageVector(self.buffer)
    def setMovingAverageDistance(self):
        self.movingAverageDistance = SetDistance([self.movingAverage], self.buffer)
    def setModelVectorsDistance(self):
        if not self.models == []:
            self.modelVectorsDistance = SetDistance(self.models, self.buffer)
        else:
            self.modelVectorsDistance = self.epsilon + self.delta
    def updateModelVectors(self):
        if self.movingAverageDistance <= self.epsilon and \
               self.movingAverageDistance <= self.modelVectorsDistance - self.delta:
            self.models.append(self.movingAverage)
    def updateWinner(self):
        min = []
        for m in self.models:
            min.append(euclideanDistance(m, self.movingAverage))
        if min == []:
            self.winner = 'No Winner'
        else:
            self.winnerIndex = Numeric.argmin(min)
            self.winner = self.models[self.winnerIndex]
            if self.recordHistory:
                self.history[str(self.time)] = self.winner[:]

    def distanceMap(self):
        map = []
        for x, y in [(x,y) for x in self.models for y in self.models]:
            map.append(euclideanDistance(x,y))
        return map
        
    def display(self):
        print "Time: ", self.time
        print "Moving average distance: ",  "%4.4f" % self.movingAverageDistance
        print "Model vectors distance: ",  "%4.4f" % self.modelVectorsDistance
        print "Moving average: "
        displayArray(self.movingAverage)
        print "Winning model vector: "
        displayArray(self.winner)
        print "Buffer: "
        for array in self.buffer:
            displayArray(array)
        print "Model vectors: "
        for array in self.models:
            displayArray(array)
        print "Model vector labels: "
        for array in self.models:
            print self.getLabel(array)
        print "Distance map: "
        displayArray(self.distanceMap(), len(self.models))
        print "History: "
        for item in self.history.iteritems():
            print "Time: ", item[0]
            print "Winner: ",
            displayArray(item[1])
            print "Label: ", self.getLabel(item[1])

    def __str__(self):
        s = ""
        s += "Time: " + str(self.time) + "\n"
        s += "Moving average distance: " +  "%4.4f " % self.movingAverageDistance + "\n"
        s += "Model vectors distance: " +  "%4.4f " % self.modelVectorsDistance + "\n"
        s += "Moving average: " + "\n"
        s += stringArray(self.movingAverage)
        s += "Winning model vector: "
        s += stringArray(self.winner)
        s += "Buffer:\n"
        for array in self.buffer:
            s += stringArray(array)
        s += "Model vectors:\n"
        for array in self.models:
            s += stringArray(array)
        s += "Model vector labels:\n"
        for array in self.models:
            s += self.getLabel(array) + "\n"
        s += "Distance map:\n"
        s += stringArray(self.distanceMap(), len(self.models))
        s += "History:\n"
        for item in self.history.iteritems():
            s += "Time: " + item[0] + "\n"
            s += "Winner: " + stringArray(item[1])
            s += "Label: " + self.getLabel(item[1]) + "\n"
        return s

    # labels!
    def getLabel(self, vector):
        """
        Returns the label associated with vector.
        """
        for w in self.labels:
            if self.compare( self.labels[w], vector ):
                return w
        return "No Label"
    def addLabel(self, word, vector):
        """
        Adds a label with key word.
        """
        if self.labels.has_key(word):
            raise NetworkError, \
                  ('Label key already in use. Call delLabel to free key.', word)
        else:
            self.labels[word] = vector
    # will raise KeyError if word is not in dict
    def delLabel(self, word):
        """
        Delete a label with key word.
        """
        del self.labels[word]
    def compare(self, v1, v2):
        """
        Compares two values. Returns 1 if all values are withing
        self.tolerance of each other.
        """
        if len(v1) != len(v2):
            return 0
        elif euclideanDistance(v1,v2) > self.tolerance:
            return 0
        else:
            return 1

class ARAVQ(RAVQ):
    """
    Extends RAVQ as described in Linaker and Niklasson.
    """
    def __init__(self, size, epsilon, delta, learningRate):
        self.alpha = learningRate
        self.deltaWinner = 'No Winner'
        self.learning = 1
        RAVQ.__init__(self, size, epsilon, delta)
    def setLearning(self, value):
        self.learning = value
    def updateDeltaWinner(self):
        if not self.winner == 'No Winner':
            if euclideanDistance(self.movingAverage, self.winner) < self.epsilon / 2:
                self.deltaWinner = self.alpha * (self.movingAverage - self.winner)
            else:
                self.deltaWinner = Numeric.zeros(len(self.winner)) 
        else:
            self.deltaWinner = 'No Winner'
    def learn(self):
        """
        Only updates the model vector, not the winner. Winner will change next time step anyway.
        """
        if self.deltaWinner != 'No Winner' and self.learning:
            self.models[self.winnerIndex] = self.winner + self.deltaWinner
        else:
            pass
    def process(self):
        RAVQ.process(self)
        self.updateDeltaWinner()
        self.learn()
        
if __name__ == '__main__':

    def makeBitList(maxbits = 8): 
        """ 
        This version is much more flexible as it relies on a general function 
        that takes any number and converts it to binary. You can make any 
        size bit representation that you want: 
        makeBitList(2) will give you: [[0, 0], [0, 1], [1, 0], [1, 1]] 
        for example. Defaults to 8 bits. 
        """ 
        retval = [] 
        for i in range((2 ** maxbits)): 
            retval.append( dec2bin(i, maxbits) ) 
        return retval 
 
    def dec2bin(val, maxbits = 8): 
        """ 
        A decimal to binary converter. Returns bits in a list. 
        """ 
        retval = [] 
        for i in range(maxbits - 1, -1, -1): 
            bit = int(val / (2 ** i)) 
            val = (val % (2 ** i)) 
            retval.append(bit) 
        return retval 

            
    bitlist = makeBitList()
    ravq = RAVQ(4, 2.1, 1.1)
    ravq.setHistory(0)
    cnt = 0
    for bits in bitlist:
        ravq.addLabel(str(cnt), bits)
        ravq.input(bits)
        cnt += 1

    print str(ravq)

    ravq = ARAVQ(4, 2.1, 1.1, .2)
    ravq.setHistory(0)
    cnt = 0
    for bits in bitlist:
        ravq.addLabel(str(cnt), bits)
        ravq.input(bits)
        cnt += 1
    print str(ravq)
