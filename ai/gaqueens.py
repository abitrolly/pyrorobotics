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
    return sum

class GAQueens(GA):
    def fitnessFunction(self, genePos):
        return fitness( self.pop[genePos].data)
                
    def isDoneFunction(self):
        return fitness( self.pop[0].data) == len(self.pop[0].data)

class MyGene(Gene):
    def display(self):
        for row in range(len(self.data)):
            for col in self.data:
                if col == row:
                    print "X",
                else:
                    print ".",
            print ""
        print ""
    
ga = GAQueens(Population(5000, MyGene, size = 16, mode = 'integer', max = 16))
ga.evolve()

# after 83 epochs:
# 8.00 1.00 7.00 13.00 6.00 0.00 9.00 5.00 12.00 15.00 3.00 10.00 2.00 14.00 11.00 4.00
