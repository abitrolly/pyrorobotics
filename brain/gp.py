from pyro.brain.ga import *
import pyro.system.share as share

class GPGene(Gene):
    def __init__(self, **args):
        self.bias = .6
        self.constructor = GPGene
        if args.has_key('bias'):
            self.bias = args['bias']
        # higher the bias, more likely to be shallow
        if (random.random() < self.bias):
            self.data = share.terminals[ int(random.random() * len(share.terminals))]
        else:
            pos = int(random.random() * len(share.operators)) 
            self.data = [share.operators[ pos ], ]
            for i in range( share.operands[ share.operators[pos] ] ):
                self.data.append( GPGene(**args).data )

    def eval_tree(self, values, tree = ''):
        if tree == '':
            tree = self.data
        if type(tree) == type('string') and values.has_key(tree):
            return values[tree]
        elif type(tree) == type( [1,]) and type(tree[0]) == type('s') and share.operands.has_key( tree[0] ):
            return self.applyOpList( values, tree )
        else:
            raise "unknownTreeType", tree

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
        else:
            raise "unknownOperator: ", mylist[0]

    def depth(self, tree = ''):
        if tree == '':
            tree = self.data
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

    def mutate(self, **args):
        total_points = self.countPoints()
        rand = int(random.random() * (total_points - 1)) + 1
        #self.data = self.replaceSymbol( rand, self.constructor(bias = self.bias).data)

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

    def crossover(self, otherGene, **args):
        term1 = self.countPoints()
        term2 = otherGene.countPoints()
        rand1 = int(term1 * random.random()) + 1
        rand2 = int(term2 * random.random()) + 1
        subtree = otherGene.getTree( rand2 )
        return self.replaceTree( rand1, subtree )

    def replaceSymbol(self, pos, replacement = '???'):
        self.replace = 0
        return self.replaceSymbolHelper(pos, self.data, replacement)
    
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
        return self.getTreeHelper(self.data, pos)

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
        self.countPoint( self.data, what )
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
            tree = self.data
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
    share.operands  = {'+'   : 2,
                       '-'   : 2,
                       '*'   : 2,
                       '/'   : 2 }

    class GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population( cnt, GPGene, **args))
    
        def fitnessFunction(self, pos):
            score = 0
            for i in range(len(values)):
                set, goal = values[i], goals[i]
                item  = self.pop.data[pos].eval_tree(set) - goal
                score += abs(item)
            return -score
    
        def isDoneFunction(self):
            return self.fitnessFunction(0) == 0
    
    gp = GP(300, bias = .6)
    gp.evolve()
    print " -----------------------------------------------------------------"

    class PI_GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population( cnt, GPGene, **args))
    
        def fitnessFunction(self, pos, pr = 0):
            val = self.pop.data[pos].eval_tree(values) 
            score  = abs(val - 3.1415)
            if pr:
                print val
            return -score
                
        def isDoneFunction(self):
            return self.fitnessFunction(0, 1) == 0

    share.operators = ['+', '-', '*', '/']
    # how many operands (arguments):
    share.operands  = {'+'   : 2,
                       '-'   : 2,
                       '*'   : 2,
                       '/'   : 2 }
    share.terminals = ['s0', 's1']
    values = {'s0' : 0.1, 's1' : 0.2}
    gp = PI_GP(1000, bias = .6)
    gp.evolve()
    print " -----------------------------------------------------------------"
