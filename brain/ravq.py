import Numeric, math, random

version = '1.3'

# general functions
def averageVector(V):
    """
    Determines the average vector of a set of vectors V.
    """
    return Numeric.add.reduce(V) / len(V)

def euclideanDistance(x, y, mask):
    """
    Takes two Numeric vectors as arguments.
    d(x, y) = sqrt(Sum[i = 1 to |x|]{(x_i - y_i) ^ 2 * mask_i})
    """
    return math.sqrt(Numeric.add.reduce( ((x - y)  ** 2) * mask))

def SetDistance(V, X, mask):
    """
    d(V, X) = (1/|X|) Sum[i = 1 to |X|]{ min[j = 1 to |V|] {|| x_i - v_j||} }
    where x_i is in X and v_j is in V.  
    """
    min = []
    sum = 0
    for x in X:
        for v in V:
            min.append(euclideanDistance(x,v,mask))
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

# these are both for determining the size of the history buffer
def isIterable(x):
    """
    Convenience function.
    """
    try:
        iter(x)
    except:
        return 0
    else:
        return 1

def nestedLength(list, recurseLimit):
    """
    Since characters in a string are iterable, we have to be careful
    to avoid an infinite loop here.
    """
    if recurseLimit == 0:
        return 1
    else:
        sum = 0
        for x in list:
            if type(x) == type('string'):
                sum += 1
            elif isIterable(x):
                sum += nestedLength(x, recurseLimit - 1)
            else:
                sum += 1
        return sum
        

def logBaseTwo(value):
    """
    Returns integer ceil of log_2 of value.
    Python 2.3 should support different log bases.
    """
    if value < 2:
        return 1
    else:
        return int(math.ceil(math.log(value)/math.log(2)))

def makeOrthogonalBitList(maxbits = 8):
    """
    Used in autolabelling ravq vectors.
    """
    retval = []
    for i in range(maxbits):
        retval.append(dec2bin(2 ** i, maxbits))
    return retval

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

def makeNoisyList(ls, percentNoise=0.1, minVal=0.0, maxVal=1.0):
    """
    Returns a noisy version of the given list, and assumes a range
    of values between 0.0 and 1.0.
    """
    retval = []
    for i in range(len(ls)):
        if random.random() < 0.5:
            retval.append(max(ls[i] - (random.random() * percentNoise), minVal))
        else:
            retval.append(min(ls[i] + (random.random() * percentNoise), maxVal))
    return retval

def makeNoisySequence(sequence, repeat, percentNoise=0.1):
    """
    Returns a noisy version of the given sequence, with each item
    repeated the number of times designated by the repeat variable.
    """
    retval = []
    for i in range(len(sequence)):
        for j in range(repeat):
            retval.append(makeNoisyList(sequence[i], percentNoise))
    return retval

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
        self.newWinnerIndex = -1
        self.previousWinnerIndex = -1
        self.verbosity = 0
        self.labels = {}
        self.recordHistory = 0
        self.history = [] # last inputs to map to each model vector
        self.historySize = 5
        self.winnerIndexHistory = [] # records the model indicies
        self.winnerHistory = [] # not implemented yet
        self.tolerance = delta
        self.counters = []
        self.addModels = 1
        self.winnerCount = 0
        self.totalCount = 0
        self.printDistance = 0
      
    # update the RAVQ
    def input(self, vec):
        """
        Drives the ravq. For most uses, the vector categorization
        is as simple as calling ravq.input(vec) on all vec in the
        dataset. Accessing the winning model vector (after the buffer
        is full) can be done directly. Using the get commands after
        calling input will return any information necessary from the
        ravq.
        """
        if self.verbosity > 1:
            print "Step:", self.time
            print vec
        array = Numeric.array(vec, 'd')
        if self.time < self.size:
            if self.verbosity > 1:
                print "filling buffer"
            self.buffer.append(array)
            if self.time == 0:
                if not self.__dict__.has_key('mask'):
                    self.mask = Numeric.ones(len(array), 'd')
                else:
                    pass # mask has already been set
        else:
            self.buffer = self.buffer[1:] + [array]
            self.process() # process new information
        if self.verbosity > 2: print self
        self.time += 1

    # attribute methods
    def getNewWinner(self):
        """
        Returns boolean depending on whether or not there is a new
        winner after the last call to input.
        """
        if self.winnerCount > 0:
            return 0
        else:
            return 1
    def setMask(self, mask):
        """
        The mask serves to weight certain components of the inputs in
        the distance calculations.
        """
        self.mask = Numeric.array(mask, 'd')
    def getWinnerCount(self):
        """
        Returns the number of times the current winner has been the
        winner, ie. the number of consecutive calls to input where the
        current winner has been the winner.
        """
        return self.winnerCount
    def getHistorySize(self):
        """
        Sets the size of each history list associated with a model
        vector. Records the previous inputs that mapped to that model
        vector, up to historySize.
        """
        return self.historySize
    def getHistoryLength(self):
        """
        Returns the total length of all histories as if history were a
        flat list.
        """
        # used to limit flat searches of history with getHistory()
        #return self.historySize * len(self.history) 
        return nestedLength(self.history, 2)
    def getHistory(self, index, colFirst = 1):
        """
        Index into history as if history were a flat list. Note that
        this method iterates across columns.
        """
        if colFirst:
            i = index % len(self.history)
            # here the mod is for the case where the history isn't full yet
            j = (index / len(self.history)) % len(self.history[i])
        else:
            i = (index / len(self.history)) % len(self.history)
            j = index % len(self.history[i])
        return self.history[i][j]
    def getWinnerTotalCount(self):
        """
        Get the total number of times the current winner has been a
        winner (not consecutive).
        """
        if self.counters == []:
            return 0
        else:
            return self.counters[self.newWinnerIndex]
    def getMinimumCount(self):
        """
        Get the minimum count that any model vector has, i.e. the
        minimum number of times any model vector has won.
        """
        if self.counters == []:
            return 0
        else:
            return self.counters[Numeric.argmin(self.counters)]
    def getMinimumVector(self):
        """
        Get the minimum model vector, i.e. the model vector that has
        won the least amount of times.
        """
        if self.models == []:
            return []
        else:
            return self.models[Numeric.argmin(self.counters)]
    def getTotalCount(self):
        """
        Total number of times a winner has been calculated.
        """
        if self.counters == []:
            return 0
        else:
            return Numeric.add.reduce(self.counters)
    def getWinnerIndex(self):
        """
        Index of current winner in self.models.
        """
        return self.newWinnerIndex
    def setVerbosity(self, value):
        """
        Determines which print statements to call.
        Debugging only.
        """
        self.verbosity = value
    def setHistory(self, value):
        """
        RAVQ will record history for each model vector consisting of
        the last inputs that mapped to that model vector. Note that
        these are inputs and not moving averages, and so for large
        buffers, the inputs may not map correctly.
        """
        self.recordHistory = value
    def setHistorySize(self, value):
        """
        Size of each history associated with a model vector.
        """
        self.historySize = value
    def setTolerance(self, value):
        """
        Used to retrieve labels.
        """
        self.tolerance = value
    def setAddModels(self, value):
        """
        Allows the RAVQ to dynamically add model vectors.
        """
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
        if self.verbosity > 1:
            print "Moving average:", self.movingAverage
        self.setMovingAverageDistance()
        self.setModelVectorsDistance()
        if self.addModels:
            self.updateModelVectors()
        self.updateWinner()
        self.updateHistory()
    def setMovingAverage(self):
        """
        Determine moving average.
        """
        self.movingAverage = averageVector(self.buffer)
    def setMovingAverageDistance(self):
        """
        How close is the moving average to the current inputs?
        """
        self.movingAverageDistance = SetDistance([self.movingAverage], self.buffer, self.mask)
    def setModelVectorsDistance(self):
        """
        How close are the model vectors to the current inputs?
        """
        if not self.models == []:
            self.modelVectorsDistance = SetDistance(self.models, self.buffer, self.mask)
        else:
            self.modelVectorsDistance = self.epsilon + self.delta
    def updateModelVectors(self):
        """
        Update models vectors with moving average if the moving
        average is the best model of the inputs.
        """
        if self.movingAverageDistance <= self.epsilon and \
               self.movingAverageDistance <= self.modelVectorsDistance - self.delta:
            self.models.append(self.movingAverage)
            self.counters.append(0)
            if self.verbosity > 1:
                print 'Adding model vector', self.movingAverage
                print 'Moving avg dist', self.movingAverageDistance
                print 'Model vec dist', self.modelVectorsDistance
    def updateWinner(self):
        """
        Calculate the current winner based on which model vector is
        closest to the moving average.
        """
        min = []
        for m in self.models:
            min.append(euclideanDistance(m, self.movingAverage, self.mask))
        if min == []:
            self.winner = 'No Winner'
        else:
            self.previousWinnerIndex= self.newWinnerIndex
            self.newWinnerIndex = Numeric.argmin(min)
            if self.previousWinnerIndex == self.newWinnerIndex:
                self.winnerCount += 1
            else:
                self.winnerCount = 0
                if len(self.winnerIndexHistory) < len(self.models):
                    self.winnerIndexHistory.append(self.newWinnerIndex)
                else:
                    self.winnerIndexHistory = self.winnerIndexHistory[1:] + \
                                         [self.newWinnerIndex]
            self.winner = self.models[self.newWinnerIndex]
            self.counters[self.newWinnerIndex] += 1
            self.totalCount += 1
    def retrieveWinner(self, vector):
        """
        Given a vector return the closest matching model vector and its index.
        """
        min = []
        array = Numeric.array(vector)
        for m in self.models:
            min.append(euclideanDistance(m, array, self.mask))
        if min == []:
            self.winner = 'No Winner'
        else:
            index = Numeric.argmin(min)
            return index, self.models[index]
    def allModels(self):
        """
        Returns a list of model vectors in index order.
        """
        models = []
        for m in self.models:
            models.append(m.tolist())
        return models
    def updateHistory(self):
        """
        Record a history of where inputs map.
        """
        if self.recordHistory and self.winner != 'No Winner':
            # new model vector so we initialize new history list
            if len(self.history) < len(self.models):
                self.history.append([self.buffer[len(self.buffer)-1]])
            # previous model vector, but corresponding history list is not full
            elif len(self.history[self.newWinnerIndex]) < self.historySize:
                self.history[self.newWinnerIndex].append(self.buffer[len(self.buffer)-1])
            # previous model vector, history list is full
            else:
                self.history[self.newWinnerIndex] = self.history[self.newWinnerIndex][1:] + \
                                                    [self.buffer[ len(self.buffer)-1]]
    def distanceMap(self):
        """
        Calculate distance map.
        """
        map = []
        for x, y in [(x,y) for x in self.models for y in self.models]:
            map.append(euclideanDistance(x,y,self.mask))
        return map

    def __str__(self):
        """
        To display ravq just call print <instance>.
        """
        s = ""
        s += "Settings:\n"
        s += "Delta: " + str(self.delta) + " Epsilon: " + str(self.epsilon) + " Buffer Size: " + str(self.size) + "\n"
        s += "Time: " + str(self.time) + "\n"
        if self.verbosity > 0:
            s += "Moving average distance: " +  "%4.4f " % self.movingAverageDistance + "\n"
            s += "Model vectors distance: " +  "%4.4f " % self.modelVectorsDistance + "\n"
            s += "Moving average:\n"
            s += "   " + stringArray(self.movingAverage)
            s += "Last winning model vector:\n"
            s += "   " + stringArray(self.winner)
            s += "Last winning label:\n"
            s += "   " + self.getLabel(self.winner) + "\n"
            s += self.bufferString()
        s += self.modelString()
        #s += self.labelString()
        if self.printDistance:
            s += "Distance map:\n"
            s += stringArray(self.distanceMap(), 1, len(self.models))
        if self.verbosity > 0:
            if self.recordHistory:
                s += self.historyString()
        return s

    def saveRAVQToFile(self, filename):
        import pickle
        fp = open(filename, 'w')
        pickle.dump(self, fp)
        fp.close()

    def loadRAVQFromFile(self, filename):
        import pickle
        fp = open(filename, 'r')
        self = pickle.load(fp)

    def openLog(self, filename):
        self.logName = filename
        self.log = open(filename, 'w')
    def closeLog(self):
        self.log.close()
        del self.log
        del self.logName

    # used so pickle will work
    def __getstate__(self):
        odict = self.__dict__.copy() 
        if odict.has_key('log'):
            del odict['log']
        return odict
    def __setstate__(self,dict):
        if dict.has_key('logName'):
            try:
                self.log = open(dict['logName'], 'a')
            except:
                pass #temporary
        self.__dict__.update(dict)

    # logging methods
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

    # helpful string methods, see __str__ method for use.
    def modelString(self):
        s = ""
        cnt = 0
        totalCount = 0
        for array in self.models:
            s += "Model: " + stringArray(array) 
            s += "Count: " + str(self.counters[cnt])
            totalCount += self.counters[cnt]
            s += "\n\n"
            cnt += 1            
        return ("%d Model vectors:\n" % cnt) + s + "Total mapped vectors: %d\n\n" % totalCount
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
        s = "History:\n"
        for pair in zip(self.models,self.history):
            s += "Model:\n" + stringArray(pair[0])
            s += "Input History:\n"
            for l in pair[1]:
                s += stringArray(l)
        return s

    # labels!
    def getVector(self, label):
        """
        Should return the model vector associated with the label.
        """
        return self.labels[label]
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
    def delAllLabels(self):
        """
        Clears the labels dictionary.
        """
        self.labels = {}
    def compare(self, v1, v2):
        """
        Compares two values. Returns 1 if all values are withing
        self.tolerance of each other.
        """
        if len(v1) != len(v2):
            return 0
        elif euclideanDistance(v1,v2, self.mask) > self.tolerance:
            return 0
        else:
            return 1
    def labelSize(self):
        """
        Returns the size of largest label. Useful for processing
        labels with a network.
        """
        max = 0
        for l in self.labels:
            if len(l) > max:
                max = len(l)
        return max
    def autoLabel(self, mode = 'binary'):
        """
        Label model vectors with strings.
        """
        import string
        if not self.models == []:
            self.delAllLabels()
            if mode == 'binary':
                labels = makeBitList(logBaseTwo(len(self.models)))
                if self.verbosity > 1: print labels
                if self.verbosity > 1: print self.labels
                for x in range(len(self.models)):
                    self.addLabel(string.join([str(y) for y in labels[x]], ''), self.models[x])
            elif mode == 'orthogonal':
                labels = makeOrthogonalBitList(len(self.models))
                if self.verbosity > 1: print labels
                if self.verbosity > 1: print self.labels
                for x in range(len(self.models)):
                    self.addLabel(string.join([str(y) for y in labels[x]], ''), self.models[x])
            elif mode == 'decimal':
                if self.verbosity > 1: print labels
                if self.verbosity > 1: print self.labels
                for x in range(len(self.models)):
                    self.addLabel(str(x), self.models[x])
            else:
                print 'Unsupported mode...not making labels.'
        else:
            print 'No models. Labels cannot be made.'

class ARAVQ(RAVQ):
    """
    Extends RAVQ as described in Linaker and Niklasson.
    """
    def __init__(self, size, epsilon, delta, learningRate):
        self.alpha = learningRate
        self.deltaWinner = 'No Winner'
        self.learning = 1
        RAVQ.__init__(self, size, epsilon, delta)
    def __str__(self):
        s = RAVQ.__str__(self)
        return s[:10] + "Alpha (learning rate): " + str(self.alpha) + " " + s[10:]
    def setLearning(self, value):
        self.learning = value
    def updateDeltaWinner(self):
        if not self.winner == 'No Winner':
            if self.verbosity > 3:
                print 'MAandW' , euclideanDistance(self.movingAverage, self.winner, self.mask)
                print 'MA' ,  self.movingAverageDistance
                print 'MV' ,  self.modelVectorsDistance
                print 'MVMD' ,  self.modelVectorsDistance - self.delta
            if euclideanDistance(self.movingAverage, self.winner, self.mask) < self.epsilon / 2:
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
            self.models[self.newWinnerIndex] = self.models[self.newWinnerIndex] + \
                                               self.deltaWinner
        else:
            pass 
    def process(self):
        """
        Here we add the new learning methods.
        """
        RAVQ.process(self)
        self.updateDeltaWinner()
        self.learn()

class ExperimentalRAVQ(ARAVQ):
    """
    Depart from the approach by Fredrik Linaker and Lars
    Niklasson. Use the current input to determine the winning model
    vector instead of the moving average. The moving average is only
    used to create model vectors in this case.
    """
    def input(self, vec):
        """
        Update current input each time input is called to be used to
        calculate winner.
        """
        self.currentInput = Numeric.array(vec)
        ARAVQ.input(self, vec)
    def updateWinner(self):
        """
        Update winner based on the current input and not the moving average.
        """
        min = []
        for m in self.models:
            min.append(euclideanDistance(m, self.currentInput, self.mask))
        if min == []:
            self.winner = 'No Winner'
        else:
            self.previousWinnerIndex= self.newWinnerIndex
            self.newWinnerIndex = Numeric.argmin(min)
            if self.previousWinnerIndex == self.newWinnerIndex:
                self.winnerCount += 1
            else:
                self.winnerCount = 0
                if len(self.winnerIndexHistory) < len(self.models):
                    self.winnerIndexHistory.append(self.newWinnerIndex)
                else:
                    self.winnerIndexHistory = self.winnerIndexHistory[1:] + \
                                         [self.newWinnerIndex]
            self.winner = self.models[self.newWinnerIndex]
            self.counters[self.newWinnerIndex] += 1
            self.totalCount += 1
    def updateHistory(self):
        """
        Record a history of where inputs map.
        """
        if self.recordHistory and self.winner != 'No Winner':
            # new model vector so we initialize new history list
            if len(self.history) < len(self.models):
                self.history.append([self.currentInput[:]])
            # previous model vector, but corresponding history list is not full
            elif len(self.history[self.newWinnerIndex]) < self.historySize:
                self.history[self.newWinnerIndex].append(self.currentInput[:])
            # previous model vector, history list is full
            else:
                self.history[self.newWinnerIndex] = self.history[self.newWinnerIndex][1:] + \
                                                    [self.currentInput[:]]
        
if __name__ == '__main__':

    print "Creating a RAVQ using all possible lists of 8 bits"
    print "------------------------------------------------------------"
    bitlist = makeBitList()
    #parameters are buffer size, epsilon, and delta
    ravq = RAVQ(4, 2.1, 1.1)
    ravq.setHistory(1)
    cnt = 0
    for bits in bitlist:
        ravq.addLabel(str(cnt), bits)
        ravq.input(bits)
        cnt += 1
    print ravq

    print "Creating an adaptive RAVQ using all possible lists of 8 bits"
    print "------------------------------------------------------------"
    ravq = ARAVQ(4, 2.1, 1.1, .2)
    ravq.setHistory(1)
    ravq.setHistorySize(2)
    cnt = 0
    #ravq.setMask([1,0,0,0,1,0,0,0])
    index = 0
    for bits in bitlist:
        ravq.addLabel(str(cnt), bits)
        ravq.input(bits)
        if ravq.getHistoryLength() > 0:
            ravq.getHistory(index) # test history features
            index = (index + 1) % ravq.getHistoryLength() 
        cnt += 1
    print ravq

    print "Creating a RAVQ using a sequence of real-valued lists"
    print "------------------------------------------------------------"
    seq = makeNoisySequence([[0.0, 0.5, 1.0],
                             [0.5, 0.5, 0.5],
                             [1.0, 0.1, 0.1],
                             [0.9, 0.9, 0.9],
                             [0.3, 0.3, 0.8]], 5, 0.05)
    ravq = RAVQ(4, 2.1, 0.5)
    ravq.setVerbosity(2)
    ravq.setHistory(1)
    ravq.setHistorySize(2)
    for i in range(len(seq)):
        ravq.input(seq[i])
    print ravq
    
    print "Test the masking capability and distance measures"
    print "------------------------------------------------------------"
    print ravq.mask
    # test masking functionality in euclidean distance calc's
    print euclideanDistance(Numeric.array([1,2]),
                            Numeric.array([3,5]),
                            Numeric.array([1,0]))
    # test order of getHistory calls
    for x in range(8):
        print stringArray(ravq.getHistory(x),0)

    print ravq
    ravq.saveRAVQToFile('test.ravq')
    ravq.loadRAVQFromFile('test.ravq')
    print ravq

