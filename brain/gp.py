from pyro.brain.ga import *
from math import pi
import pyro.system.share as share

class GPGene(Gene):
    def __init__(self, **args):
        self.bias = .6
        self.fitness = 0.0
        self.args = args
        self.mode = -1
        if args.has_key('bias'):
            self.bias = args['bias']
        # higher the bias, more likely to be shallow
        if (random.random() < self.bias):
            self.genotype = share.terminals[ int(random.random() * len(share.terminals))]
        else:
            pos = int(random.random() * len(share.operators)) 
            self.genotype = [share.operators[ pos ], ]
            for i in range( share.operands[ share.operators[pos] ] ):
                self.genotype.append( GPGene(**args).genotype )

    def mutate(self, mutationRate):
        """
        Depending on the mutationRate, will mutate particular terminal.
        """
        # this is about as hacky as one can get
        total_points = self.countPoints()
        terminal_points = self.countPoints('terminal')
        rand = int(random.random() * (terminal_points - 1)) + 1
        terms = 0
        for i in range(1, total_points + 1):
            subtree = self.getTree(i)
            if type(subtree) == type('i2'):
                terms += 1
                if terms == rand:
                    randterm = GPGene( **self.args)
                    newgenotype = self.replaceTree(i, randterm.genotype)
                    self.genotype = newgenotype
                    return
        

    def crossover(self, parent2, crossoverRate):
        parent1 = self
        term1 = parent1.countPoints()
        term2 = parent2.countPoints()
        rand1 = int(term1 * random.random()) + 1
        rand2 = int(term2 * random.random()) + 1
        subtree1 = parent1.getTree( rand1 )
        subtree2 = parent2.getTree( rand2 )
        p1 = deepcopy( parent1 )
        p2 = deepcopy( parent2 )
        p1.replaceTree(rand1, subtree1 )
        p2.replaceTree( rand2, subtree2 )
        return p1, p2
               
    def eval_tree(self, values, tree = ''):
        if tree == '':
            tree = self.genotype
        if type(tree) == type('string') and values.has_key(tree):
            return values[tree]
        elif type(tree) == type( [1,]) and type(tree[0]) == type('s') and share.operands.has_key( tree[0] ):
            try:
                retval = self.applyOpList( values, tree )
            except "unknownOperator":
                retval = self.applyUserDefinedOplist( values, tree )
            return retval
        else:
            raise "unknownTreeType", tree

    def applyUserDefinedOplist(self, values, mylist):
        if share.userOperators.has_key( mylist[0] ):
            func = share.userOperators[ mylist[0] ]
            eval_tree = lambda obj: self.eval_tree( values, obj )
            args = map( eval_tree,  mylist[1:] )
            return apply(func, args)
        else:
            raise "unknownUserOperator", mylist[0]

    def applyOpList(self, values, mylist):
        if mylist[0] == 'and':
            if self.eval_tree(values, mylist[1]) and self.eval_tree(values, mylist[2]):
                return 1
            else:
                return 0
        elif mylist[0] == 'or':
            if self.eval_tree(values, mylist[1]) or self.eval_tree(values, mylist[2]):
                return 1
            else:
                return 0
        elif mylist[0] == '+':
            return self.eval_tree(values, mylist[1]) + self.eval_tree(values, mylist[2])
        elif mylist[0] == '-':
            return self.eval_tree(values, mylist[1]) - self.eval_tree(values, mylist[2])
        elif mylist[0] == '*':
            return self.eval_tree(values, mylist[1]) * self.eval_tree(values, mylist[2])
        elif mylist[0] == '/':
            operand1 = self.eval_tree(values, mylist[1])
            operand2 = self.eval_tree(values, mylist[2])
            if operand2 != 0:
                return operand1 / operand2
            else:
                return 0.0
        elif mylist[0] == 'ifpos':
            testExp = self.eval_tree(values, mylist[1])
            if testExp > 0:
                return self.eval_tree(values, mylist[2])
            else:
                return self.eval_tree(values, mylist[3])
        else:
            raise "unknownOperator", mylist[0]

    def depth(self, tree = ''):
        if tree == '':
            tree = self.genotype
        if tree in share.terminals:
            return 0
        elif tree[0] in share.operators:
            max_depth = 0
            for o in range(1, share.operands[ tree[0] ] + 1):
                deep = self.depth(tree[o])
                if deep > max_depth:
                    max_depth = deep
            return 1 + max_depth
        else:
            raise "unknownTreetype", tree

    def replaceTree( self, pos, subtree ):
        # first, replace symbol at pos with a special marker
        retval1 = self.replaceSymbol(pos, '???')
        # next, recurse through, find it and replace with subtree
        retval2 = self.replaceTreeHelper(retval1, '???', subtree)
        return retval2

    def replaceTreeHelper(self, lyst, old, new):
        if type(lyst) == type([1,]):
            retval = []
            for i in range(len(lyst)):
                retval.append(self.replaceTreeHelper( lyst[i], old, new))
            return retval
        else:
            if lyst == old:
                return new
            else:
                return lyst

    def replaceSymbol(self, pos, replacement = '???'):
        self.replace = 0
        return self.replaceSymbolHelper(pos, self.genotype, replacement)
    
    def replaceSymbolHelper(self, pos, tree, replacement):
        self.replace += 1
        if tree in share.terminals:
            if self.replace == pos:
                return replacement
            else:
                return tree
        elif tree[0] in share.operators:
            if self.replace == pos:
                return replacement
            else:
                retval = [tree[0], ]
                for i in range(share.operands[ tree[0] ]):
                    retval.append( self.replaceSymbolHelper(pos, tree[i + 1], replacement))
                return retval
        else:
            raise "unknownTreetype", tree

    def getTree(self, pos):
        self.points = 0
        return self.getTreeHelper(self.genotype, pos)

    def getTreeHelper(self, tree, pos):
        if tree in share.terminals:
            self.points += 1
            if self.points == pos:
                return tree
        elif tree[0] in share.operators:
            self.points += 1
            if self.points == pos:
                return tree
            for o in range(1, share.operands[ tree[0] ] + 1):
                retval = self.getTreeHelper(tree[o], pos)
                if self.points >= pos:
                    return retval
        else:
            raise "unknownTreetype", tree

    def countPoints(self, what = 'all'):
        self.points = 0
        self.countPoint( self.genotype, what )
        return self.points

    def countPoint(self, tree, what = 'all'):
        if tree in share.terminals:
            if what == 'all' or what == 'terminal':
                self.points += 1
        elif tree[0] in share.operators:
            if what == 'all' or what == 'operator':
                self.points += 1
            for o in range(1, share.operands[ tree[0] ] + 1):
                self.countPoint(tree[o], what)
        else:
            raise "unknownTreetype", tree

    def display(self, tree = ''):
        if tree == '':
            tree = self.genotype
        if tree in share.terminals:
            print tree,
        elif tree[0] in share.operators:
            print "(%s " % tree[0],
            for o in range(1, share.operands[ tree[0] ] + 1):
                self.display(tree[o])
            print ")",
        else:
            raise "unknownTreetype", tree


if __name__ == '__main__':
    share.terminals = ['i1', 'i2']
    # inputs for XOR:
    values = [ {'i1' : 0, 'i2' : 0},
               {'i1' : 0, 'i2' : 1},
               {'i1' : 1, 'i2' : 0},
               {'i1' : 1, 'i2' : 1} ]
    goals = [ 0, 1, 1, 0 ] # outputs for XOR
    # These go together:
    share.operators = ['+', '-', '*', '/']
    # how many operands (arguments):
    share.operands  = {'+'     : 2,
                       '-'     : 2,
                       '*'     : 2,
                       '/'     : 2,
                       'ifpos' : 3,
                       'and'   : 2,
                       'or'    : 2}
    class GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population( cnt, GPGene, bias =.6,
                                          elitePercent = .1, verbose = 1),
                        verbose = 1)
    
        def fitnessFunction(self, pos):
            diff = 0
            for i in range(len(values)):
                set, goal = values[i], goals[i]
                item  = self.pop.individuals[pos].eval_tree(set) - goal
                diff += abs(item)
            return max(4 - diff, 0)
    
        def isDone(self):
            fit = self.pop.bestMember.fitness
            self.pop.bestMember.display()
            print 
            return fit == 4
    
    gp = GP(50)
    gp.evolve()
    print " -----------------------------------------------------------------"
    raw_input("Press enter to continue...")
    class PI_GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population(cnt, GPGene, bias = .6,
                                         verbose = 1, elitePercent = .1),
                        verbose = 1, maxGeneration = 25)
        def fitnessFunction(self, pos, pr = 0):
            diff = abs(self.pop.individuals[pos].eval_tree(values) - pi)
            if pr:
                self.pop.individuals[pos].display()
                print
            return max(pi - diff, 0) 
                
        def isDone(self):
            return abs(self.fitnessFunction(0, 1) - pi) < .001

    share.operators = ['+', '-', '*', '/', 'ifpos', 'and', 'or', '+1']
    share.operands['+1'] = 1
    share.terminals = ['1', 'e']
    share.userOperators = {'+1': lambda obj: obj + 1 }
    values = {'1' : 1, 'e' : math.e}
    gp = PI_GP(100)
    gp.evolve()
    print " -----------------------------------------------------------------"
