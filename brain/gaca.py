
from ca import *
from ga import *

data = Lattice(height = 500)
rules = Rules()
generation = 0

def fitnessFunc(gene):
    rules.data[0] = gene
    totalSteps = 0
    testCases = 5.0
    for i in range(1, testCases): # 1-9
        data.randomize(i / testCases)
        p = poisson(149)
        print "Running for", p, "steps...",
        steps = rules.applyAll(data, p)
        print "done:", steps,
        if steps < p:
            d = data.density(steps)
            print "density:", d,
            if i / testCases < .5 and d == 0.0:
                totalSteps += steps
                print "correct!"
            elif i / testCases >= .5 and d == 1.0:
                totalSteps += steps
                print "correct!"
            else:
                print "wrong....."
        else:
            print "steps >= p"
    print "=============================", totalSteps
    return totalSteps

def isDoneFunc(genes):
    return 0
        
ga = GA(makeRandomPop(50, 2 ** 7, 0, -1), fitnessFunc, isDoneFunc)
ga.integer = 1
ga.evolve()
ga.pop[0].display()
