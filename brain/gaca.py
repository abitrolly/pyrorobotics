
from ca import *
from ga import *

class GACA(GA):
    def __init__(self):
        GA.__init__(self, makeRandomPop(100, 2 ** 7, 0, -1))
        self.lattice = Lattice(height = 500)
        self.rules = Rules()
        self.integer = 1
        self.crossoverPercent = .8

    def fitnessFunction(self, genePos):
        self.rules.data[0] = self.pop[genePos]
        totalSteps = 0
        testCases = 100.0
        method = 'correct' # 'complexity'
        for i in range(1, testCases): # 1-9
            self.lattice.randomize(i / testCases)
            p = poisson(149)
            print "Running for", p, "steps...",
            steps = self.rules.applyAll(self.lattice, p)
            print "done:", steps,
            if steps < p:
                d = self.lattice.density(steps)
                print "density:", d,
                if method == 'complexity':
                    if i / testCases < .5 and d == 0.0:
                        totalSteps += steps
                        print "correct!"
                    elif i / testCases >= .5 and d == 1.0:
                        totalSteps += steps
                        print "correct!"
                    else:
                        print "wrong"
                elif method == 'correct':
                    if i / testCases < .5 and d == 0.0:
                        totalSteps += 1
                        print "correct!"
                    elif i / testCases >= .5 and d == 1.0:
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
        return 0

if __name__ == '__main__':
    ga = GACA()
    ga.evolve()
    ga.pop[0].display()
