"""

Governor code for self regulating networks.

"""



import pyro.brain.ravq
import random

class Governor:

    def __init__(self, size = 5, epsilon = 0.2, delta = 0.6, mask = [], bufferSize = 50):
        # ravq
        self.ravq = pyro.brain.ravq.RAVQ(size, epsilon, delta)
        self.ravq.setHistory(0)
        self.ravq.setAddModels(1)
        if not mask == []: 
            self.ravq.setMask(mask)

        # buffer 
        self.buffer = []
        self.bufferSize = bufferSize
        self.bufferIndex = 0

    def process(self, vector):
        self.ravq.input(vector)
        if self.ravq.getNewWinner(): 
            if len(self.buffer) >= self.bufferSize:
                self.buffer = self.buffer[1:] + [vector]
            else:
                self.buffer.append(vector)
        if len(self.buffer) > 0: 
            array = self.buffer[self.bufferIndex]
            self.bufferIndex = (self.bufferIndex + 1) % len(self.buffer)
            return array
        else:
            return vector

    def __len__(self):
        return len(self.ravq.models)

    def query(self):
        return str(self.ravq)
    
    def save(self, filename):
        self.ravq.saveRAVQToFile(filename)

    def load(self, filename):
        self.ravq.loadRAVQFromFile(filename)


class AdaptiveGovernor(Governor):

    def __init__(self, size = 5, epsilon = 0.2, delta = 0.6, alpha = 0.02, mask = [], bufferSize = 50):
        # ravq
        self.ravq = pyro.brain.ravq.ARAVQ(size, epsilon, delta, alpha)
        self.ravq.setHistory(0)
        self.ravq.setAddModels(1)
        if not mask == []: 
            self.ravq.setMask(mask)

        # buffer 
        self.buffer = []
        self.bufferSize = bufferSize
        self.bufferIndex = 0

class BalancingGovernor(Governor):

    def __init__(self, size = 5, epsilon = 0.2, delta = 0.6, alpha = 0.02, mask = [], depth = 5):
        # ravq
        self.ravq = pyro.brain.ravq.ARAVQ(size, epsilon, delta, alpha)
        self.ravq.setHistory(1)
        self.ravq.setHistorySize(depth)
        self.ravq.setAddModels(1)
        if not mask == []: 
            self.ravq.setMask(mask)
        self.index = -1

    def process(self, vector):
        self.ravq.input(vector)
        if self.ravq.getHistoryLength() is 0:
            return vector
        else:
            self.index = (1 + self.index) % self.ravq.getHistoryLength()
            return self.ravq.getHistory(self.index)

    # Definition borrowed from conx.py: I want to randomize the order
    # of training across the buffers periodically, but when to do so
    # is yet another parameter, so this is not yet implimented.
    
    def randomIndices(self, number):
        """
        random list generator
        """
        self.indices = [0] * number
        flag = [0] * number
        for i in range(number):
            pos = int(random.random() * number)
            while (flag[pos] == 1):
                pos = int(random.random() * number)
            flag[pos] = 1
            self.indices[pos] = i   

class DiscreteGovernor:

    def __init__(self, sampleDelay, bufferSize):
        self.delay = sampleDelay
        self.counter = 0

        # buffer 
        self.buffer = []
        self.bufferSize = bufferSize
        self.bufferIndex = 0

    def process(self, vector):
        if self.counter % self.delay == 0: 
            if len(self.buffer) >= self.bufferSize:
                self.buffer = self.buffer[1:] + [vector]
            else:
                self.buffer.append(vector)
        self.counter += 1
        if len(self.buffer) > 0: 
            array = self.buffer[self.bufferIndex]
            self.bufferIndex = (self.bufferIndex + 1) % len(self.buffer)
            return array
        else:
            return vector

    def query(self):
        pass
    
    def save(self, filename):
        pass

    def load(self, filename):
        pass
        

class RandomGovernor:

    # for random sampling
    def flip(self):
        """
        Flip a biased coin.
        """
        return random.random() <= self.probability


    def exponential(self):
        """
        Sample from discrete exponential distribution.
        """
        value = random.expovariate(1.0/10.0)
        return int(value)

    def waitTime(self):
        """
        Discrete distribution based on histogram data.
        """
        listp = [ 0.00595745,  0.0093617,   0.02553191,  0.04425532, 0.05787234,  0.08085106,
                  0.14382979,  0.2212766,   0.31829787, 0.39744681, 0.46893617,  0.53531915,
                  0.61531915,  0.70468085,  0.7787234 ,  0.85361702, 0.90468085,  0.92851064,
                  0.94808511,  0.95744681,  0.96255319,  0.96510638, 0.97361702,  0.98297872,
                  0.9906383 ,  0.99659574,  1.00]

        
        randomnumber = random.random()
        for i in range(len(listp)):
            if randomnumber < listp[i]:
                break
        return i

    def __init__(self, probability, bufferSize):
        self.probability = probability

        # buffer 
        self.buffer = []
        self.bufferSize = bufferSize
        self.bufferIndex = 0
        self.wait = self.waitTime()

    def process(self, vector):
        if self.wait is 0:
            self.wait = self.waitTime() # reset wait
            if len(self.buffer) >= self.bufferSize:
                self.buffer = self.buffer[1:] + [vector]
            else:
                self.buffer.append(vector)
        else:
            self.wait -= 1 # decrement wait
        # decide what to return
        if len(self.buffer) > 0: 
            array = self.buffer[self.bufferIndex]
            self.bufferIndex = (self.bufferIndex + 1) % len(self.buffer)
            return array
        else:
            return vector

    def query(self):
        pass
    
    def save(self, filename):
        pass

    def load(self, filename):
        pass

if __name__ == '__main__':

    import os
    import gzip
    from pyro.brain.conx import *

    # read in experimental training data
    locationfile = gzip.open('location.dat.gz', 'r')
    sensorfile = gzip.open('sensors.dat.gz', 'r')

    sensors = sensorfile.readlines()
    locations = locationfile.readlines()

    locationfile.close()
    sensorfile.close()

    # create network
    net = Network()
    inSize = len(map(lambda x: float(x), sensors[0].rstrip().split()))
    #print inSize    

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
      
    # create governor

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
    
    govMask = [1] * (inSize - 1) + [16] + [inSize/4] * 4
    governor = BalancingGovernor(ravqBuffer, govEpsilon, delta, alpha, govMask, govBuffer)

    #print govMask
    #print len(govMask)

    for i in range(5000):
        sensorlist = map(lambda x: float(x), sensors[i].rstrip().split())
        locationlist = map(lambda x: float(x), locations[i].rstrip().split())
        array = governor.process(sensorlist + locationlist)
        error, correct, total = net.step(input = array[:inSize], output = array[inSize:])
        if i % 100 == 0:
            print "Step: ", i
            print error, correct, total
        

    print governor.query()
