# ------------------------------------------------
# A simple Genetic Algorithm in Python
# (See bottom for examples, and tests)
# ------------------------------------------------
# (c) D.S. Blank, Bryn Mawr College 2001
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

def displayln(v):
    print v

def makeRandomGene(size, real = 1, bias = .5):
    # Possible Change: Initialization is made beween -1, and 1
    gene = []
    for i in range(size):
        if real:
            gene.append( random.random() * 2.0 - 1.0)
        else:
            gene.append( random.random() < bias)
    return gene

def makeRandomPop(cnt, size, real = 1, bias = .5):
    pop = []
    for i in range(cnt):
        if bias == -1:
            pop.append( makeRandomGene(size, real, float(i) / cnt) )
        else:
            pop.append( makeRandomGene(size, real, bias) )
    return pop

def sum(a):
    # FIX: I think this is built in somewhere
    sum = 0
    for n in a:
        sum += n
    return sum

# The classes:

class GA:
    """
    Class which defines everything needed to run a GA.
    """
    def __init__(self, population, batch = 0):
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.pop = population
        self.popsize = len(population)
        self.geneLength = len(population[0])
        self.fitness = [0.0] * self.popsize
        self.mutationRate = 0.05
        self.crossoverRate = 0.3
        self.maxEpoch = 0
        self.batch = batch
        self.integer = 0
        self.generation = 0

    def isDoneFunction(self):
        pass

    def fitnessFunction(self, genePosition):
        pass

    def applyFitnessFunction(self):
        for i in range( self.popsize ):
            self.fitness[i] = self.fitnessFunction(i)

    def setSeed(self, value):
        self.seed1 = value
        self.seed2 = value / 23.45
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))

    def swap(self, a, b):
        t = self.fitness[a]
        self.fitness[a] = self.fitness[b]
        self.fitness[b] = t
        t = self.pop[a]
        self.pop[a] = self.pop[b]
        self.pop[b] = t

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
        self.quickSort(0, self.popsize - 1)
        # FIX: have two sorts (minimize, maximize)
        #self.fitness.reverse()
        #self.pop.reverse()

    def display(self, i = -1):
        if i == -1:
            print "Pop    :"
            for p in range(len(self.pop)):
                map(lambda v: display("%3.2f" % v), self.pop[p])
                print "Fitness:", self.fitness[p]
        else:
            map(lambda v: display("%3.2f" % v), self.pop[i])
            print "Fitness:", self.fitness[i]

    def probability(self, pos):
        return ((self.popsize - pos) + 0.0) / self.popsize

    def pick(self, type):
	p = int(random.random() * self.popsize)
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

    def sweep(self):
        self.applyFitnessFunction() # sets self.fitness
        self.sort()
        self.crossover()
        self.mutate()

    def crossover(self):
        """
        If crossoverRate = .3, then .3 of pop will be replaced.
        """
        number = int(self.crossoverRate * self.popsize)
        for i in range(number):
            g1 = self.pick(GOOD)
            g2 = self.pick(GOOD)
            b1 = self.pick(BAD)
            cross = int(random.random() * self.geneLength)
            temp = self.pop[g1][:cross]
            temp.extend(self.pop[g2][cross:])
            self.pop[b1] = temp
            
    def mutate(self):
        """
        If mutationRate = .1, then .1 of the pop will get mutated.
        If self.integer, flip bit
        Else mutate with momentum (+- previous value)
        """
        number = int(self.mutationRate * self.popsize)
        for i in range(number):
            rand = self.pick(RANDOM)
            pos = int(random.random() * self.geneLength)
            if self.integer:
                self.pop[rand][pos] = not self.pop[rand][pos]
            else:
                r = random.random()
                if (r < .25):
                    self.pop[rand][pos] -= random.random()
                elif (r < .50):
                    self.pop[rand][pos] += random.random()
                elif (r < .75):
                    self.pop[rand][pos] = random.random()
                else:
                    self.pop[rand][pos] = -random.random()
    
    def evolve(self):
        self.generation = 0
        while (self.generation < self.maxEpoch or self.maxEpoch == 0):
            self.generation += 1
            self.sweep()
            print "-" * 30
            print "Epoch #", self.generation, ":"
            print "Best : (position # 0 )"
            self.display(0)
            print "Median: (position #", self.popsize/2, ")"
            self.display(self.popsize/2)
            print "Worst: (position #", self.popsize - 1, ")"
            self.display(self.popsize - 1)
            if self.isDoneFunction():
                print "Completed!"
                return

if __name__ == '__main__':
    # Here is a test to evolve a list of big numbers:
    from pyro.brain.conx import *
    class TestGA(GA):
        def fitnessFunction(self, genePos):
            return sum(self.pop[genePos])
        def isDoneFunction(self):
            return sum(self.pop[0]) > 20

    # Here is a test to evolve the weights/biases in a neural network
    # that solves the XOR problem:

    class NNGA(GA):
        def __init__(self):
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
            GA.__init__(self, makeRandomPop(300, len(g)))
        def fitnessFunction(self, genePos):
            self.network.unArrayify(self.pop[genePos])
            error, correct, count = self.network.sweep()
            return -error
        def isDoneFunction(self):
            self.network.unArrayify(self.pop[0])
            error, correct, count = self.network.sweep()
            print "Correct:", correct
            return correct == 4


    print "Do you want to evolve a list of big numbers? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = TestGA(makeRandomPop(300, 10))
        ga.evolve()

    print "Do you want to evolve a neural network that can do XOR? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = NNGA()
        ga.evolve()
        ga.network.unArrayify(ga.pop[0])
        ga.network.setInteractive(1)
        ga.network.sweep()

