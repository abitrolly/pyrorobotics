# --------------------------------------------------------------------------
# A simple Genetic Algorithm in Python
# (See bottom for examples, and tests)
# --------------------------------------------------------------------------
# (c) D.S. Blank, Bryn Mawr College 2003
#
# Updated 4/29/03 by Lisa Meeden
# There are a few key differences in this version.
#
# 1. There is no longer a GA parameter selectionRate.  The next generation
#    of individuals is created by selecting two parents at a time from the
#    current population.  The crossoverRate determines how often those two
#    parents will be recombined to produce two new children.  For example,
#    if the crossoverRate is 0.6 that means that 60% of the time the parents
#    will be crossed and 40% of the time they will simply be copied.  The
#    mutationRate determines how often each gene is likely to be modified.
#    For example, if the mutationRate is 0.1 that means that 10% of the
#    individual genes will be modified.  So in a genotype of length 50, 
#    approximately five of the genes will be mutated.
#
# 2. We are now using a roulette wheel method of selection.  Therefore,
#    the fitness function must return a non-negative value.  
# --------------------------------------------------------------------------

import RandomArray, Numeric, math, random, time, sys
from copy import deepcopy

def display(v):
    print v,

def sum(a):
    sum = 0
    for n in a:
        sum += n
    return sum

def flip(probability):
    """
    Flip a biased coin
    """
    return random.random() <= probability


# The classes:
#  Gene - specifics of gene representation 
#  Population - collection of Genes
#  GA - the parameters of evolution

class Gene:
    def __init__(self, **args):
        self.verbose = 0
        self.genotype = []
        self.fitness = 0.0
        self.mode = 'float'
        self.bias = 0.5
        self.min = 0 # inclusive
        self.max = 1 # inclusive
        if args.has_key('verbose'):
            self.verbose = args['verbose']
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
                self.genotype.append( (random.random() * (self.max - self.min)) + self.min)
            else:
                raise "unknownMode", self.mode

    def __getitem__(self, val):
        return self.genotype[val]

    def __len__(self):
        return len(self.genotype)

    def display(self):
        if self.mode == 'bit' or self.mode == 'integer': 
            map(lambda v: display(int(v)), self.genotype)
        elif self.mode == 'float':
            map(lambda v: display("%3.2f" % v), self.genotype)
        else:
            raise "unknownMode", self.mode

class Population:
    def __init__(self, cnt, geneConstructor, **args):
        self.sumFitness = 0   
        self.avgFitness = 0   
        self.individuals = []
        self.eliteMembers = []
        self.elitePercent = 0.0
        self.bestMember = -1
        self.size = cnt
        self.geneConstructor = geneConstructor
        self.args = args
        self.verbose = 0
        if args.has_key('elitePercent'):
            self.elitePercent = args['elitePercent']
        if args.has_key('verbose'):
            self.verbose = args['verbose']
        for i in range(cnt):
            self.individuals.append(geneConstructor(**args))

    def __getitem__(self, val):
        return self.individuals[val]

    def __len__(self):
        return len(self.individuals)

    def select(self):
        """
        Select a single individual via the roulette wheel method.
        Algorithm from Goldberg's book, page 63.  NOTE: fitness
        function must return positive values to use this method
        of selection.
        """
        index = 0
        partsum = 0.0
        if self.sumFitness == 0:
            raise "Population has a total of zero fitness"
        spin = random.random() * self.sumFitness
        while index < self.size-1:
            fitness = self.individuals[index].fitness
            if fitness < 0:
                raise "Negative fitness in select", fitness
            partsum += self.individuals[index].fitness
            if partsum >= spin:
                break
            index += 1
        if self.verbose > 2:
            print "selected",
            self.individuals[index].display(),
            print "fitness", self.individuals[index].fitness
        return self.individuals[index]

    def mutate(self, child, mode, mutationRate):
        """
        Depending on the mutationRate, will mutate particular genes
        in the child.
        """
        for i in range(len(child)):
            if flip(mutationRate):
                if self.verbose > 2:
                    print "mutating at position", i
                if mode == 'bit': 
                    child[i] = not child[i]
                elif mode == 'integer': 
                    r = random.random()
                    if (r < .5):
                        child[i] += 1
                    else:
                        child[i] -= 1
                elif mode == 'float': 
                    r = random.random()
                    if (r < .5):
                        child[i] -= random.random()
                    else:
                        child[i] += random.random()
                else:
                    raise "unknownMode", mode
    
    def crossover(self, parent1, parent2, crossoverRate):
        """
        Depending on the crossoverRate, will return two new children
        created by crossing over the given parents at a single point,
        or will return copies of the parents.
        """
        geneLength = len(parent1.genotype)
        if flip(crossoverRate):
            crosspt = (int)((random.random() * (geneLength - 2)) + 1)
            if self.verbose > 2:
                print "crossing over at point", crosspt
            child1 = parent1.genotype[:crosspt]
            child1.extend(parent2.genotype[crosspt:])
            child2 = parent2.genotype[:crosspt]
            child2.extend(parent1.genotype[crosspt:])
            return child1, child2
        else:
            if self.verbose > 2:
                print "no crossover"
            return parent1.genotype[:], parent2.genotype[:]

    def statistics(self):
        """
        Maintains important statistics about the current population.
        It calculates total fitness, average fitness, best fitness,
        and worst fitness.  Also stores the best individual in
        the variable self.bestMember.
        """
        self.sumFitness = 0
        best = self.individuals[0]
        bestPosition = 0
        worst= self.individuals[0]
        self.eliteMembers = self.individuals[0:int(self.elitePercent * len(self.individuals))]
        self.eliteMembers.sort(lambda x, y: cmp( x.fitness, y.fitness))
        for i in range(self.size):
            current = self.individuals[i]
            current.position = i
            self.sumFitness += current.fitness
            if current.fitness < worst.fitness:
                worst = current
            if current.fitness > best.fitness:
                best = current
                bestPosition = i
            if len(self.eliteMembers) > 0 and current.fitness > self.eliteMembers[0].fitness:
                self.eliteMembers.append( current )
                self.eliteMembers.sort(lambda x, y: cmp( x.fitness, y.fitness))
                self.eliteMembers = self.eliteMembers[1:]
        self.bestMember = deepcopy(best)
        self.avgFitness = (self.sumFitness * 1.0) / self.size
        if self.verbose > 0:
            print "Fitness: Total", "%7.2f" % self.sumFitness, 
            print "Best", "%5.2f" % best.fitness,
            print "Average", "%5.2f" % self.avgFitness,
            print "Worst", "%5.2f" % worst.fitness

class GA:
    """
    Class which defines everything needed to run a GA.
    """
    def __init__(self, population, **args):
        self.mutationRate = 0.1
        self.crossoverRate = 0.6
        self.maxGeneration = 0
        self.generation = 0
        self.verbose = 0
        if args.has_key('verbose'):
            self.verbose = args['verbose']
        if args.has_key('mutationRate'):
            self.mutationRate = args['mutationRate']
        if args.has_key('selectionRate'):
            self.selectionRate = args['selectionRate']
        if args.has_key('crossoverRate'):
            self.crossoverRate = args['crossoverRate']
        if args.has_key('maxGeneration'):
            self.maxGeneration = args['maxGeneration']
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.pop = population
        self.applyFitnessFunction()
        if self.verbose > 0:
            print "-" * 60
            print "Initial population"
        self.pop.statistics()
        if self.verbose > 1:
            self.display()

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

    def display_one(self, p):
        self.pop.individuals[p].display()
        print "Fitness:", self.pop.individuals[p].fitness

    def display(self):
        print "Population:"
        for p in range(len(self.pop.individuals)):
            self.display_one(p)

    def generate(self):
        """
        Iteratively creates a new population from the current population.
        Selects two parents, attempts to cross them, and then attempts to
        mutate the resulting children.  The probability of these operations
        occurring is determined by the crossoverRate and the mutationRate.
        Overwrites the old population with the new population.
        """
        mode = self.pop.individuals[0].mode
        newpop = range(self.pop.size)
        i = 0
        while i < self.pop.size - 1:
            parent1 = self.pop.select()
            parent2 = self.pop.select()
            newpop[i], newpop[i+1] = self.pop.crossover(parent1, parent2, self.crossoverRate)
            self.pop.mutate(newpop[i], mode, self.mutationRate)
            self.pop.mutate(newpop[i+1], mode, self.mutationRate)
            i += 2
        # For odd sized populations, need to create the last child
        if self.pop.size % 2 == 1:
            newpop[self.pop.size-1] = self.pop.select().genotype[:]
            self.pop.mutate(newpop[self.pop.size-1], mode, self.mutationRate)
        # Copy new generation into population
        elitePositions = map( lambda x: x.position, self.pop.eliteMembers)
        for i in range(self.pop.size):
            if i not in elitePositions:
                self.pop.individuals[i].genotype = newpop[i][:]
    
    def evolve(self):
        self.generation = 0
        while self.generation < self.maxGeneration or self.maxGeneration == 0:
            self.generation += 1
            if self.verbose > 0:
                print "-" * 60
                print "Generation", self.generation
            self.generate()
            self.applyFitnessFunction()
            self.pop.statistics()
            if self.verbose > 1:
                self.display()
            if self.isDone():
                break
        print "-" * 60
        print "Done evolving at generation", self.generation
        print "Current best individual"
        self.pop.bestMember.display()
        print "Fitness", self.pop.bestMember.fitness

if __name__ == '__main__':
    # Here is a test to evolve a list of integers to maximize their sum:

    class MaxSumGA(GA):
        def fitnessFunction(self, i):
            return sum(self.pop.individuals[i].genotype)
        def isDone(self):
            return self.pop.bestMember.fitness > 30

    print "Do you want to evolve a list of integers to maximize their sum? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print
        ga = MaxSumGA(Population(15, Gene, size=10, mode='integer',
                                 verbose=1, elitePercent = .1),
                      mutationRate=0.1, crossoverRate=0.5, verbose=1,
                      maxGeneration=50)
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
            n.setLearning(0)
            g = n.arrayify()
            self.network = n
            GA.__init__(self,
                        Population(cnt, Gene, size=len(g), verbose=1,
                                   min=-1, max=1, elitePercent = .1),
                        mutationRate=0.5, crossoverRate=0.25,
                        maxGeneration=400, verbose=1)
        def fitnessFunction(self, genePos):
            self.network.unArrayify(self.pop.individuals[genePos].genotype)
            error, correct, count = self.network.sweep()
            return 4 - error
        def isDone(self):
            self.network.unArrayify(self.pop.bestMember.genotype)
            error, correct, count = self.network.sweep()
            print "Correct:", correct
            return correct == 4

    print "Do you want to evolve a neural network that can do XOR? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = NNGA(20)
        ga.evolve()
        ga.network.unArrayify(ga.pop.bestMember.genotype)
        ga.network.setInteractive(1)
        ga.network.sweep()

