# ------------------------------------------------
# A simple Genetic Algorithm in Python
# (See bottom for examples, and tests)
# ------------------------------------------------
# (c) D.S. Blank, Bryn Mawr College 2003
# ------------------------------------------------

# Assumptions:
#   1. rates: mutation .05 %, crossover .3 %
#   2. Maximizes the fitness function

import RandomArray, Numeric, math, random, time, sys

# Some useful local functions, and variables:

RANDOM = 0
GOOD = 1
BAD = 2

def display(v):
    print v,

def sum(a):
    sum = 0
    for n in a:
        sum += n
    return sum

def avg(seq):
    sum = 0.0
    for i in range(len(seq)):
        sum += seq[i]
    return sum / len(seq)


# The classes:
#  Population - collection of Gene (shouldn't have to change)
#  Gene - specifics of gene representation (subclass this)
#  GA - the parameters of evolution (shouldn't have to change)

class Gene:
    def __init__(self, **args):
        # Possible Change: Initialization is made beween -1, and 1
        self.data = []
        self.mode = 'float'
        self.bias = 0.5
        self.min = 0 # inclusive
        self.max = 1 # inclusive
        if args.has_key('min'):
            self.min = args['min']
        if args.has_key('max'):
            self.max = args['max']
        if args.has_key('mode'):
            self.mode = args['mode']
        if args.has_key('bias'):
            self.bias = args['bias']
        for i in range(args['size']):
            if self.mode == 'bit':
                self.data.append( random.random() < self.bias)
            elif self.mode == 'integer':
                self.data.append( math.floor(random.random() * (self.max - self.min + 1)) + self.min)
            elif self.mode == 'float':
                self.data.append( random.random() * (self.max - self.min + 1) + self.min)
            else:
                raise "unknownMode", self.mode

    def __getitem__(self, val):
        return self.data[val]

    def __len__(self):
        return len(self.data)

    def fitnessFunction(self, **args):
        # Overload this, or the one in GA.
        pass

    def crossover(self, otherGene, **args):
        """
        Takes another gene, produces a mixture, and returns it.
        """
        if (random.random() < .5): # single point
            crosspoint = int(random.random() * len(self.data))
            temp = self.data[:crosspoint]
            temp.extend(otherGene.data[crosspoint:])
        else: # uniform
            temp = self.data[:] # copy self
            for i in range(len(self.data)):
                if random.random() < .5: # from other
                    temp[i] = otherGene.data[i]
        return temp

    def display(self):
        map(lambda v: display("%3.2f" % v), self.data)

    def mutate(self, **args):
        """
        If mutationRate = .1, then .1 of the pop will get mutated.
        If self.mode == integer, flip bit
        Else mutate with momentum (+- previous value) or
        other amount
        """
        pos = int(random.random() * len(self.data))
        if self.mode == 'bit': # flip it
            self.data[pos] = not self.data[pos]
        elif self.mode == 'integer': 
            r = random.random()
            if (r < .33):
                self.data[pos] += 1
            elif (r < .66):
                self.data[pos] -= 1
            else:
                self.data[pos] = math.floor(random.random() * (self.max - self.min + 1)) + self.min
        elif self.mode == 'float': 
            r = random.random()
            if (r < .33):
                self.data[pos] -= random.random()
            elif (r < .66):
                self.data[pos] += random.random()
            else:
                self.data[pos] = random.random() * (self.max - self.min + 1) + self.min
        else:
            raise "unknownMode", self.mode
        

class Population:
    """
    Class to abstract gene-related items.
    """
    def __init__(self, cnt, geneConstructor, **args):
        self.data = []
        self.size = cnt
        self.geneConstructor = geneConstructor
        self.args = args
        for i in range(cnt):
            self.data.append( geneConstructor(**args))

    def __getitem__(self, val):
        return self.data[val]

    def __len__(self):
        return len(self.data)

    def mutate(self, rate, **args):
        for i in range(int(rate * self.size)):
            pos = self.pick(RANDOM)
            self.data[pos].mutate(**args)

    def crossover(self, rate, **args):
        """
        If crossoverRate = .3, then .3 of pop will be replaced.
        """
        for i in range(int(rate * self.size)):
            self.data[ self.pick(BAD) ].data = self.data[ self.pick(GOOD) ].crossover(self.data[ self.pick(GOOD) ], **args)

    def pick(self, type):
	p = int(random.random() * len(self.data))
        if (type == BAD):
            if (random.random() > self.probability(p)):
                return p
            else:
                return self.pick(type)
        elif (type == GOOD):
            if (random.random() < self.probability(p)):
                return p
            else:
                return self.pick(type);
        else:
            return p

    def probability(self, pos):
        return ((len(self.data) - pos) + 0.0) / len(self.data)
            
class GA:
    """
    Class which defines everything needed to run a GA.
    """
    def __init__(self, population, **args):
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.pop = population
        self.fitness = [0.0] * len(self.pop.data)
        self.mutationRate = 0.05
        self.crossoverRate = 0.3
        if args.has_key('mutationRate'):
            self.mutationRate = args['mutationRate']
        if args.has_key('crossoverRate'):
            self.crossoverRate = args['crossoverRate']
        self.maxGeneration = 0
        self.generation = 0

    def isDoneFunction(self):
        # Overload this
        pass

    def fitnessFunction(self, genePosition, **args):
        # Override this, or the one in the Gene
        return self.pop.data[genePosition].fitnessFunction(**args)

    def applyFitnessFunction(self):
        for i in range( len(self.pop.data) ):
            self.fitness[i] = self.fitnessFunction(i)

    def setSeed(self, value):
        self.seed1 = value
        self.seed2 = value / 23.45
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))

    def swap(self, a, b):
        self.fitness[a], self.fitness[b] = self.fitness[b], self.fitness[a]
        self.pop.data[a], self.pop.data[b] = self.pop.data[b], self.pop.data[a]

    def partition(self, first, last):
        pivot = self.fitness[ (first + last) / 2 ]
        while (first <= last):
            while (self.fitness[first] > pivot):
                first += 1
            while (self.fitness[last] < pivot):
                last -= 1
            if (first <= last):
                self.swap(first, last)
                first += 1
                last -= 1
        return first

    def quickSort(self, first, last):
        if (first < last ):
            piv_index = self.partition(first, last )
            self.quickSort(first, piv_index - 1 )
            self.quickSort(piv_index, last )

    def sort(self):
        self.quickSort(0, len(self.pop.data) - 1)

    def display_one(self, p):
        self.pop.data[p].display()
        print "Fitness:", self.fitness[p]

    def display(self):
        print "Population:"
        for p in range(len(self.pop.data)):
            self.display_one(p)
            
    def sweep(self):
        self.applyFitnessFunction() # sets self.fitness
        self.sort()
        self.pop.crossover(self.crossoverRate)
        self.pop.mutate(self.mutationRate)

    def evolve(self, display = 1):
        self.generation = 0
        while (self.generation < self.maxGeneration or self.maxGeneration == 0):
            self.generation += 1
            self.sweep()
            print "-" * 30
            print "Generation #", self.generation, ":"
            print "Best : (position # 0 )"
            if display: self.display_one(0)
            print "Median: (position #", len(self.pop.data)/2, ")"
            if display: self.display_one(len(self.pop.data)/2)
            print "Worst: (position #", len(self.pop.data) - 1, ")"
            if display: self.display_one(len(self.pop.data) - 1)
            if self.isDoneFunction():
                print "Completed!"
                return

if __name__ == '__main__':
    # Here is a test to evolve a list of big numbers:
    from pyro.brain.conx import *
    class TestGA(GA):
        def fitnessFunction(self, genePos):
            return sum(self.pop[genePos].data)
        def isDoneFunction(self):
            return sum(self.pop[0].data) > 20

    print "Do you want to evolve a list of big numbers? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = TestGA(Population(300, Gene, size = 10, mode = 'integer'))
        ga.evolve()

    # Here is a test to evolve the weights/biases in a neural network
    # that solves the XOR problem:

    class NNGA(GA):
        def __init__(self, cnt):
            n = Network()
            n.add( Layer('input', 2) )
            n.add( Layer('hidden', 2) )
            n.add( Layer('output', 1) )
            n.connect('input', 'hidden')
            n.connect('hidden', 'output')
            n.setInputs([[0.0, 0.0],
                         [0.0, 1.0],
                         [1.0, 0.0],
                         [1.0, 1.0]])
            n.setOutputs([[0.0],
                          [1.0],
                          [1.0],
                          [0.0]])
            n.setVerbosity(0)
            n.setTolerance(.4)
            g = n.arrayify()
            self.network = n
            GA.__init__(self, Population( cnt, Gene, size = len(g)))
        def fitnessFunction(self, genePos):
            self.network.unArrayify(self.pop.data[genePos].data)
            error, correct, count = self.network.sweep()
            return -error
        def isDoneFunction(self):
            self.network.unArrayify(self.pop.data[0].data)
            error, correct, count = self.network.sweep()
            print "Correct:", correct
            return correct == 4

    print "Do you want to evolve a neural network that can do XOR? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = NNGA(750)
        ga.evolve()
        ga.network.unArrayify(ga.pop.data[0].data)
        ga.network.setInteractive(1)
        ga.network.sweep()

