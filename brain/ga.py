# ------------------------------------------------
# A simple Genetic Algorithm in Python
# (See bottom for examples, and tests)
# ------------------------------------------------
# (c) D.S. Blank, Bryn Mawr College 2003
# updated 3/21/03 by Lisa Meeden
# ------------------------------------------------

# Assumptions:
#   1. Default rates: mutation .05 %, crossover .3 %
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
#  Population - collection of Genes
#  Gene - specifics of gene representation 
#  GA - the parameters of evolution

class Gene:
    def __init__(self, verbose = 0, **args):
        # Possible Change: Initialization is made beween -1, and 1
        self.verbose = verbose
        self.genotype = []
        self.fitness = 0.0
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
                self.genotype.append( random.random() < self.bias)
            elif self.mode == 'integer':
                self.genotype.append( math.floor(random.random() *
                                                 (self.max - self.min + 1)) + self.min)
            elif self.mode == 'float':
                self.genotype.append( random.random() *
                                      (self.max - self.min + 1) + self.min)
            else:
                raise "unknownMode", self.mode

    def __getitem__(self, val):
        return self.genotype[val]

    def __len__(self):
        return len(self.genotype)

    def crossover(self, otherGene, uniform = 0, **args):
        """
        Takes another gene, produces a mixture, and returns it.
        """
        if (not uniform): # single point
            crosspoint = int(random.random() * len(self.genotype))
            if self.verbose == 2:
                print "at position", crosspoint
            temp = self.genotype[:crosspoint]
            temp.extend(otherGene.genotype[crosspoint:])
        else:
            if self.verbose == 2:
                print "uniformily"
            temp = self.genotype[:] # copy self
            for i in range(len(self.genotype)):
                if random.random() < .5: # from other
                    temp[i] = otherGene.genotype[i]
        return temp

    def display(self):
        if self.mode == 'bit' or self.mode == 'integer': 
            map(lambda v: display(int(v)), self.genotype)
        elif self.mode == 'float':
            map(lambda v: display("%3.2f" % v), self.genotype)
        else:
            raise "unknownMode", self.mode

    def mutate(self, **args):
        pos = int(random.random() * len(self.genotype))
        if self.verbose == 2:
            print "at position", pos
        if self.mode == 'bit': 
            self.genotype[pos] = not self.genotype[pos]
        elif self.mode == 'integer': 
            r = random.random()
            if (r < .5):
                self.genotype[pos] += 1
            else:
                self.genotype[pos] -= 1
        elif self.mode == 'float': 
            r = random.random()
            if (r < .5):
                self.genotype[pos] -= random.random()
            else:
                self.genotype[pos] += random.random()
        else:
            raise "unknownMode", self.mode
        

class Population:
    """
    Class to abstract gene-related items.
    """
    def __init__(self, cnt, geneConstructor, verbose = 0, **args):
        self.individuals = []
        self.size = cnt
        self.geneConstructor = geneConstructor
        self.args = args
        self.verbose = verbose
        for i in range(cnt):
            self.individuals.append( geneConstructor(verbose, **args))

    def __getitem__(self, val):
        return self.individuals[val]

    def __len__(self):
        return len(self.individuals)

    def mutate(self, rate, **args):
        """
        If mutationRate = .1, then .1 of the pop will get mutated.
        """
        for i in range(int(rate * self.size)):
            pos = self.pick(RANDOM)
            if self.verbose  == 2:
                print "Mutation in individual", pos,
            self.individuals[pos].mutate(**args)

    def crossover(self, rate, **args):
        """
        If crossoverRate = .3, then .3 of pop will be replaced.
        """
        for i in range(int(rate * self.size)):
            replace = self.pick(BAD)
            parent1 = self.pick(GOOD)
            parent2 = self.pick(GOOD)
            if self.verbose == 2:
                print "Crossover with parent", parent1, "and", parent2,
                print "replacing individuals", replace,
            self.individuals[replace].genotype = \
                self.individuals[parent1].crossover(self.individuals[parent2], **args)

    def pick(self, type):
	p = int(random.random() * len(self.individuals))
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
        return ((len(self.individuals) - pos) + 0.0) / len(self.individuals)
            
class GA:
    """
    Class which defines everything needed to run a GA.
    """
    def __init__(self, population, verbose = 0, **args):
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.pop = population
        self.applyFitnessFunction()
        self.sort()
        self.mutationRate = 0.05
        self.crossoverRate = 0.3
        self.maxGeneration = 0
        self.generation = 0
        self.verbose = verbose
        if args.has_key('mutationRate'):
            self.mutationRate = args['mutationRate']
        if args.has_key('crossoverRate'):
            self.crossoverRate = args['crossoverRate']
        if args.has_key('maxGeneration'):
            self.maxGeneration = args['maxGeneration']

    def isDone(self):
        # Override this
        pass

    def fitnessFunction(self, genePosition, **args):
        # Override this
        pass

    def applyFitnessFunction(self):
        for i in range( len(self.pop.individuals) ):
            self.pop.individuals[i].fitness = self.fitnessFunction(i)

    def setSeed(self, value):
        self.seed1 = value
        self.seed2 = value / 23.45
        random.seed(self.seed1)
        RandomArray.seed(int(self.seed1), int(self.seed2))

    def swap(self, a, b):
        self.pop.individuals[a], self.pop.individuals[b] = \
            self.pop.individuals[b], self.pop.individuals[a]

    def partition(self, first, last):
        pivot = self.pop.individuals[(first+last)/2].fitness
        while (first <= last):
            while (self.pop.individuals[first].fitness > pivot):
                first += 1
            while (self.pop.individuals[last].fitness < pivot):
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
        self.quickSort(0, len(self.pop.individuals) - 1)

    def display_one(self, p):
        self.pop.individuals[p].display()
        print "Fitness:", self.pop.individuals[p].fitness

    def display(self):
        print "Population:"
        for p in range(len(self.pop.individuals)):
            self.display_one(p)
            
    def evolve(self):
        self.generation = 0
        while (self.generation < self.maxGeneration or self.maxGeneration == 0):
            print "-" * 30
            print "Generation #", self.generation, ":"
            if self.verbose >= 1:
                print "Best : (position # 0 )"
                self.display_one(0)
                print "Median: (position #", len(self.pop.individuals)/2, ")"
                self.display_one(len(self.pop.individuals)/2)
                print "Worst: (position #", len(self.pop.individuals) - 1, ")"
                self.display_one(len(self.pop.individuals) - 1)
            if self.verbose == 2:
                self.display()
            if self.isDone():
                print "Completed!"
                return
            self.pop.crossover(self.crossoverRate)
            self.pop.mutate(self.mutationRate)
            self.applyFitnessFunction()
            if self.verbose == 2:
                self.display()
            self.sort()
            self.generation += 1

if __name__ == '__main__':
    # Here is a test to evolve a list of integers to maximize their sum:

    class MaxSumGA(GA):
        def fitnessFunction(self, i):
            return sum(self.pop.individuals[i].genotype)
        def isDone(self):
            return self.fitnessFunction(0) > 30

    print "Do you want to evolve a list of integers to maximize their sum? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print
        ga = MaxSumGA(Population(50, Gene, size = 10, mode = 'integer'),
                      mutationRate = .2, crossoverRate = .5,
                      maxGeneration = 50, verbose = 1)
        ga.evolve()
    print 

    # Here is a test to evolve the weights/biases in a neural network
    # that solves the XOR problem:

    from pyro.brain.conx import *
    class NNGA(GA):
        def __init__(self, cnt):
            n = Network()
            n.add( Layer('input', 2) )
            n.add( Layer('hidden', 3) )
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
            GA.__init__(self, Population( cnt, Gene, size = len(g)),
                        mutationRate = 0.5, crossoverRate = 0.25,
                        maxGeneration = 400, verbose = 1)
        def fitnessFunction(self, genePos):
            self.network.unArrayify(self.pop.individuals[genePos].genotype)
            error, correct, count = self.network.sweep()
            return -error
        def isDone(self):
            self.network.unArrayify(self.pop.individuals[0].genotype)
            error, correct, count = self.network.sweep()
            print "Correct:", correct
            return correct == 4

    print "Do you want to evolve a neural network that can do XOR? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = NNGA(300)
        ga.evolve()
        ga.network.unArrayify(ga.pop.individuals[0].genotype)
        ga.network.setInteractive(1)
        ga.network.sweep()

