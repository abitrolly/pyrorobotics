from pyro.brain.ga import *

def safe_queen(new_row, new_col, sol):
    for row in range(new_row):
        if (sol[row] == new_col or
            sol[row] + row == new_col + new_row or
            sol[row] - row == new_col - new_row):
            return 0
    return 1

def fitness(sol):
    set = []
    row = 0
    sum = 0
    for col in sol:
        set.append( col )
        if col < 0 or col >= len(sol):
            return 0
        sum += safe_queen( row, col, set)
        row += 1
    previous = -1
    for col in sol:
        # see how far apart each is, normalize, add to sum
        if previous == -1:
            bonus = 0.0
        else:
            bonus += abs(col - previous)
        previous = col
    return sum + 1 - (bonus / ((len(sol) - 1) * len(sol)))
    #return sum 

class GAQueens(GA):
    def fitnessFunction(self, genePos):
        return fitness( self.pop.individuals[genePos].genotype)
                
    def isDone(self):
        self.pop[0].display()
        fit = fitness( self.pop.individuals[0].genotype)
        print "Best Fitness:", fit
        return fit == len(self.pop.individuals[0].genotype)

    def mutate(self, **args):
        pos = int(random.random() * len(self.genotype))
        if self.verbose == 2:
            print "at position", pos
        self.genotype[pos] =  math.floor(random.random() * \
                                   (self.max - self.min + 1)) + self.min

class MyGene(Gene):
    def display(self):
        for row in range(len(self.genotype)):
            for col in self.genotype:
                if col == row:
                    print "X",
                else:
                    print ".",
            print ""

if __name__ == '__main__':    
    ga = GAQueens(Population(300, MyGene, size = 16, mode = 'integer', max = 16, verbose = 1))
    ga.evolve()

# after 83 generations:
# mygene = MyGene(size = 16)
# mygene.data = [8, 1, 7, 13, 6, 0, 9, 5, 12, 15, 3, 10, 2, 14, 11, 4]
# mygene.display()
#
#  . . . . . X . . . . . . . . . .
#  . X . . . . . . . . . . . . . .
#  . . . . . . . . . . . . X . . .
#  . . . . . . . . . . X . . . . .
#  . . . . . . . . . . . . . . . X
#  . . . . . . . X . . . . . . . .
#  . . . . X . . . . . . . . . . .
#  . . X . . . . . . . . . . . . .
#  X . . . . . . . . . . . . . . .
#  . . . . . . X . . . . . . . . .
#  . . . . . . . . . . . X . . . .
#  . . . . . . . . . . . . . . X .
#  . . . . . . . . X . . . . . . .
#  . . . X . . . . . . . . . . . .
#  . . . . . . . . . . . . . X . .
#  . . . . . . . . . X . . . . . .


