import Numeric, math

version = '1.1'

# general functions
def averageVector(V):
    """
    Determines the average vector of a set of vectors V.
    """
    return Numeric.add.reduce(V) / len(V)

def euclideanDistance(x, y):
    """
    Takes two Numeric vectors as arguments.
    d(x, y) = Sum[i = 1 to |x|]{(x_i - y_i) ^ 2}
    """
    return math.sqrt(Numeric.add.reduce((x - y) ** 2))

def SetDistance(V, X):
    """
    d(V, X) = (1/|X|) Sum[i = 1 to |X|]{ min[j = 1 to |V|] {|| x_i - v_j||} }
    where x_i is in X and v_j is in V.  
    """
    min = []
    sum = 0
    for x in X:
        for v in V:
            min.append(euclideanDistance(x,v))
        sum += min[Numeric.argmin(min)]
    return sum / len(X)

def stringArray(a, newline = 1, width = 0):
    """
    String form of an array (any sequence of floats, really) to the screen.
    """
    s = ""
    cnt = 0
    if type(a) == type('string'):
        return a
    for i in a:
        s += "%4.4f " % i
        if width > 0 and (cnt + 1) % width == 0:
            s += '\n'
        cnt += 1
    if newline:
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
        self.counters = []
        self.addModels = 1

    # update the RAVQ
    def input(self, vec):
        array = Numeric.array(vec, 'd')
        if self.time < self.size:
            self.buffer.append(array)
        else:
            self.buffer = self.buffer[1:] + [array]
            self.process() # process new information
        if self.verbosity > 2: print self
        self.time += 1

    # attribute methods
    def setVerbosity(self, value):
        self.verbosity = value
    def setHistory(self, value):
        self.recordHistory = value
    def setTolerance(self, value):
        self.tolerance = value
    def setAddModels(self, value):
        self.addModels = value
        
    # process happens once the buffer is full
    def process(self):
        """
        The RAVQ Algorithm:
        1. Calculate the average vector of all inputs in the buffer.
        2. Calculate the distance of the average from the set of inputs
        in the buffer.
        3. Calculate the distance of the model vectors from the inputs
        in the buffer.
        4. If distance in step 2 is small and distance in step 3 is large,
        add current average to list of model vectors.
        5. Calculate the winning model vector based on distance between
        each model vector and the buffer list.
        6. Update history.
        ---The metric used to calculate distance is described in
        "Sensory Flow Segmentation Using a Resource Allocating
        Vector Quantizer" by Fredrik Linaker and Lars Niklasson
        (2000).---
        """
        self.setMovingAverage()
        self.setMovingAverageDistance()
        self.setModelVectorsDistance()
        if self.addModels:
            self.updateModelVectors()
        self.updateWinner()
        self.updateHistory()
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
            self.counters.append(1)
            if self.verbosity > 1:
                print 'Adding model vector', self.movingAverage
                print 'Moving avg dist', self.movingAverageDistance
                print 'Model vec dist', self.modelVectorsDistance
    def updateWinner(self):
        min = []
        for m in self.models:
            min.append(euclideanDistance(m, self.movingAverage))
        if min == []:
            self.winner = 'No Winner'
        else:
            self.winnerIndex = Numeric.argmin(min)
            self.winner = self.models[self.winnerIndex]
            self.counters[self.winnerIndex] += 1
    def updateHistory(self):
        if self.recordHistory and self.winner != 'No Winner':
            self.history[str(self.time)] = self.winner[:]
    def distanceMap(self):
        map = []
        for x, y in [(x,y) for x in self.models for y in self.models]:
            map.append(euclideanDistance(x,y))
        return map

    def __str__(self):
        """
        To display ravq just call print <instance>.
        """
        s = ""
        s += "Time: " + str(self.time) + "\n"
        s += "Moving average distance: " +  "%4.4f " % self.movingAverageDistance + "\n"
        s += "Model vectors distance: " +  "%4.4f " % self.modelVectorsDistance + "\n"
        s += "Moving average:\n"
        s += stringArray(self.movingAverage)
        s += "Winning model vector:\n"
        s += stringArray(self.winner)
        s += "Winning label:\n"
        s += self.getLabel(self.winner) + "\n"
        s += self.bufferString()
        s += self.modelString()
        s += self.labelString()
        s += "Distance map:\n"
        s += stringArray(self.distanceMap(), 1, len(self.models))
        s += self.historyString()
        return s

    def saveRAVQToFile(self, filename):
        import pickle
        fp = open(filename, 'w')
        pickle.dump(self, fp)
        fp.close()

    def openLog(self, filename):
        self.logName = filename
        self.log = open(filename, 'w')
    def closeLog(self):
        self.log.close()

    # used so pickle will work
    def __getstate__(self):
        odict = self.__dict__.copy() 
        try:
            del odict['log']
        except:
            pass
        return odict
    def __setstate__(self,dict):
        try:
            self.log = open(dict['logName'], 'a') 
            self.__dict__.update(dict)            
        except:
            pass
    
    def logHistory(self, labels = 1, tag = 'None'):
        """
        Writes time winner label tag to file in four column format.
        """
        line = str(self.time) + " " + stringArray(self.winner, 0)
        if labels:
            line += " " + self.getLabel(self.winner)
        if not tag == 'None':
            line += " " + tag + " "
        line += "\n"
        self.log.write(line)
    def logRAVQ(self):
        self.log.write(str(self))

    # helpful string methods
    def modelString(self):
        s = "Model vectors:\n"
        cnt = 0
        for array in self.models:
            s += str(self.counters[cnt]) + " "
            s += stringArray(array)
            cnt += 1
            
        return s
    def labelString(self):
        s = "Model vector labels:\n"
        for array in self.models:
            s += self.getLabel(array) + "\n"
        return s
    def bufferString(self):
        s = "Buffer:\n"
        for array in self.buffer:
            s += stringArray(array)
        return s
    def historyString(self):
        if not self.recordHistory:
            return ''
        s = "History:\n"
        for i in range(self.time):
            s += "Time: " + str(i) + "\n"
            if self.history.has_key(str(i)):
                s += "Winner: " + stringArray(self.history[str(i)])
                s += "Label: " + self.getLabel(self.history[str(i)]) + "\n"
            else:
                s += "No Winner\n"
            s += "----------------------------------------------------------\n"
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
            raise KeyError, \
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
            if self.verbosity > 3:
                print 'MAandW' , euclideanDistance(self.movingAverage, self.winner)
                print 'MA' ,  self.movingAverageDistance
                print 'MV' ,  self.modelVectorsDistance
                print 'MVMD' ,  self.modelVectorsDistance - self.delta
            if euclideanDistance(self.movingAverage, self.winner) < self.epsilon / 2:
                self.deltaWinner = self.alpha * (self.movingAverage - self.winner)
                if self.verbosity > 4: print 'Learning'
            else:
                self.deltaWinner = Numeric.zeros(len(self.winner)) 
        else:
            self.deltaWinner = 'No Winner'
    def learn(self):
        """
        Only updates the model vector, not the winner. Winner will change
        next time step anyway.
        """
        if self.deltaWinner != 'No Winner' and self.learning:
            self.models[self.winnerIndex] = self.models[self.winnerIndex] + self.deltaWinner
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

    print ravq

    ravq = ARAVQ(4, 2.1, 1.1, .2)
    ravq.setHistory(0)
    cnt = 0
    for bits in bitlist:
        ravq.addLabel(str(cnt), bits)
        ravq.input(bits)
        cnt += 1

    print ravq