
from pyro.general.ca import *
from pyro.brain.ga import *

class GACA(GA):
    def __init__(self, cnt, **args):
        self.rules = Rules()
        self.lattice = Lattice(height = 500, size = 100)
        GA.__init__(self, Population( cnt, Gene, **args), **args)
        self.integer = 1
        self.crossoverPercent = .8

    def fitnessFunction(self, genePos):
        self.rules.data[0] = self.pop.individuals[genePos].genotype
        totalSteps = 0
        testCases = 8
        method = 'complexity' # 'correct' or 'complexity'
        for i in range(0, testCases + 1): # 1-9
            self.lattice.randomize(i / float(testCases))
            p = poisson(149)
            print "Running for", p, "steps...",
            steps = self.rules.applyAll(self.lattice, p)
            #print
            #self.lattice.display()
            print "done:", steps,
            if steps < p:
                d = self.lattice.density(steps)
                print "density:", d,
                if method == 'complexity':
                    if i / float(testCases) < .5 and d == 0.0:
                        totalSteps += steps
                        print "correct!"
                    elif i / float(testCases) >= .5 and d == 1.0:
                        totalSteps += steps
                        print "correct!"
                    else:
                        print "wrong"
                elif method == 'correct':
                    if i / float(testCases) < .5 and d == 0.0:
                        totalSteps += 1
                        print "correct!"
                    elif i / float(testCases) >= .5 and d == 1.0:
                        totalSteps += 1
                        print "correct!"
                    else:
                        print "wrong"
                else:
                    raise "InvalidScoringMethod", method
            else:
                print "steps >= p wrong"
        print self.generation, genePos, "============================= Density:", self.rules.density(0), 'Fitness:', totalSteps
        return totalSteps

    def isDoneFunction(self):
        print "Best:", self.pop.bestMember.fitness
        self.pop.bestMember.display()
        return 0

if __name__ == '__main__':
    ga = GACA(10, elitePercent = .1, size = 2 ** 7, mode = 'bit', bias = .1)
    ga.evolve()
