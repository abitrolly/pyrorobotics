from pyro.brain.ga import *
import pyro.system.share as share
from math import pi
import operator, sys

### WORKAROUND: deepcopy can't copy dicts with functions
### Currently using global share.env to avoid having it
### in gene
### FIX: don't use deepcopy

def parse(exp, env):
    if type(exp) == type( (1,) ):
        return GPTree(*map(lambda x: parse(x,env), exp))
    else:
        return env.env[exp]

def div_func(*operands):
    if operands[1] == 0:
        return sys.maxint # not all python's have "infinity"
    else:
        return operands[0] / float(operands[1])
def ifpos_func(operands, env):
    test_val, if_val, else_val = operands
    test_result = test_val.eval(env)
    if (test_result):
        return if_val.eval(env)
    else:
        return else_val.eval(env)
def and_func(operands, env):
    if len(operands) == 0:
        return 1
    else:
        car = operands[0].eval(env)
        if not car:
            return 0
        else:
            return and_func(operands[1:], env)
def or_func(operands, env):
    if len(operands) == 0:
        return 0
    else:
        car = operands[0].eval(env)
        if car:
            return 1
        else:
            return or_func(operands[1:], env)
class Operator:
    def __init__(self, func, operands, type = "regular"):
        self.func = func
        self.operands = operands
        self.type = type

class Environment:
    def __init__(self, dict = {}):
        self.env = dict.copy()
    def update(self, dict):
        self.env.update( dict )
    def terminals(self):
        retvals = {}
        for item in self.env:
            if not isinstance(self.env[item], Operator):
                retvals[item] = self.env[item]
        return retvals
    def operators(self):
        retvals = {}
        for item in self.env:
            if isinstance(self.env[item], Operator):
                retvals[item] = self.env[item]
        return retvals
    def lazyOps(self):
        retvals = {}
        for item in self.env:
            if isinstance(self.env[item], Operator) and self.env[item].type == "lazy":
                retvals[item] = self.env[item]
        return retvals
    def regularOps(self):
        retvals = {}
        for item in self.env:
            if isinstance(self.env[item], Operator) and self.env[item].type == "regular":
                retvals[item] = self.env[item]
        return retvals
        
class GPTree:
    def __init__(self, op, *children):
        self.op = op
        self.children = []
        for child in children:
            if not isinstance(child, GPTree):
                self.children.append(GPTree(child))
            else:
                self.children.append(child)
        self.internals = [0] * len(self.children)
        self.externals = [0] * len(self.children)
        self.resetCounts()
    def leaf(self):
        return len(self.children) == 0
    def getTerminalTree(self, pos):
        if pos == 0 and self.leaf():
            return self
        cnt = 0
        for i in range(len(self.children)):
            if pos < self.externals[i] + cnt:
                return self.children[i].getTerminalTree(pos - cnt)
            cnt += self.externals[i]
    def __str__(self):
        s = ''
        if self.leaf():
            s += "%s" % self.op
        else:
            s += "(%s" % self.op
            for child in self.children:
                s += " %s" % child
            s += ")"
        return s
    def resetCounts(self):
        i = 0
        for child in self.children:
            internal, ext = child.resetCounts()
            self.internals[i] = internal
            self.externals[i] = ext
            i += 1
        if self.leaf():
            return (0,1)
        else:
            return (reduce(operator.add, self.internals, 1),
                    reduce(operator.add, self.externals, 0))
    def eval(self, env = Environment()):
        #print "Evaluating:", self, "in", env
        if self.leaf():
            if self.op in env.env:
                retval = env.env[self.op]
            else:
                retval = self.op
        else:
            if self.op in env.lazyOps().keys():
                op = env.lazyOps()[self.op].func
                #print "   apply (lazy):", op, self.children
                retval = apply(op, (self.children, env))
            elif self.op in env.regularOps().keys():
                op = env.env[self.op].func
                results = map(lambda x: x.eval(env), self.children)
                #print "   apply (regular):", op, results
                retval = apply(op, results)
            else:
                # just a terminal
                retval = env.env[self.op]
        #print "Evaluated:", retval
        return retval

class GPGene(Gene):
    def __init__(self, **args):
        self.bias = .6
        self.fitness = 0.0
        self.mode = -1
        self.args = args  # can't have env in it
        if args.has_key('bias'):
            self.bias = args['bias']
        # higher the bias, more likely to be shallow
        if (random.random() < self.bias):
            terminals = share.env.terminals().keys()
            if len(terminals) == 0:
                raise AttributeError, "no terminals given in environment or eval()"
            self.genotype = GPTree(terminals[ int(random.random() * len(terminals))])
        else:
            operators = share.env.operators().keys()
            if len(operators) == 0:
                raise AttributeError, "no operators in environment"
            pos = int(random.random() * len(operators)) 
            treeArgs = [operators[ pos ], ]
            for i in range( share.env.env[operators[pos]].operands ):
                treeArgs.append( GPGene(**args).genotype )
            self.genotype = GPTree( *treeArgs )
            #print self.genotype
    #def copy(self):
    #    return self # the func in the env are a problem
    def display(self):
        print self.genotype
    def eval(self, additionalEnv = {}):
        share.env.update(additionalEnv)
        return self.genotype.eval(share.env)
    def mutate(self, mutationRate):
        """
        Depending on the mutationRate, will mutate particular terminal.
        """
        if self.genotype.leaf():
            terminal_points = 1
        else:
            terminal_points = reduce(operator.add, self.genotype.externals, 0)
        rand = int(random.random() * terminal_points)
        subtree = self.genotype.getTerminalTree(rand) # return Tree
        temp = GPGene( **self.args)
        self.replaceTree(subtree, temp.genotype)
        self.genotype.resetCounts()
    def replaceTree(self, subtree, temp):
        subtree.op = temp.op
        subtree.children = temp.children
        subtree.internals = temp.internals
        subtree.externals = temp.externals
        del temp
    def crossover(self, parent2, crossoverRate):
        parent1 = self
        if parent1.genotype.leaf():
            term1 = 1
        else:
            term1 = reduce(operator.add, parent1.genotype.externals, 0)
        if parent2.genotype.leaf():
            term2 = 1
        else:
            term2 = reduce(operator.add, parent2.genotype.externals, 0)
        rand1 = int(term1 * random.random())
        rand2 = int(term2 * random.random())
        subtree1 = parent1.genotype.getTerminalTree( rand1 )
        subtree2 = parent2.genotype.getTerminalTree( rand2 )
        p1 = deepcopy( parent1 )
        p2 = deepcopy( parent2 )
        self.replaceTree(p2, subtree1 )
        self.replaceTree(p1, subtree2 )
        return p1, p2
               
# A standard environment:
env = {'+'  : Operator(operator.add, 2, "regular"),
       '-'  : Operator(operator.sub, 2, "regular"),
       '*'  : Operator(operator.mul, 2, "regular"),
       '/'  : Operator(div_func,     2, "regular"),
       'ifpos' : Operator(ifpos_func,3, "lazy"),
       'and'   : Operator(and_func,  2, "lazy"),
       'or'    : Operator(or_func,   2, "lazy"),
       }

if __name__ == '__main__':
    share.env = Environment(env)
    share.env.update( {'i1':0, 'i2':0} )
    exp = GPTree('+', GPTree('-', GPTree('-', GPTree('-', 'i1', 'i2'), 'i1'), 'i1'), GPTree('ifpos', 'i1', GPTree('ifpos', GPTree('/', 'i2', 'i2'), 'i1', 'i2'), GPTree('*', GPTree('*', 'i1', 'i2'), GPTree('or', 'i1', 'i2'))))

    class GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population( cnt, GPGene, bias =.6, 
                                          elitePercent = .1, verbose = 1),
                        verbose = 1)
    
        def fitnessFunction(self, pos):
            #print "Computing Fitness of", self.pop.individuals[pos].genotype
            outputs = [ 0, 1, 1, 0 ] # outputs for XOR
            inputs = [ {'i1' : 0, 'i2' : 0},
                       {'i1' : 0, 'i2' : 1},
                       {'i1' : 1, 'i2' : 0},
                       {'i1' : 1, 'i2' : 1} ]
            diff = 0
            for i in range(len(inputs)):
                #print "Computing Fitness with", inputs[i]
                set, goal = inputs[i], outputs[i]
                retval = self.pop.individuals[pos].eval(set)
                #print "result:", retval
                item  = retval - goal
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
                                         verbose = 1, 
                                         elitePercent = .1),
                        verbose = 1, maxGeneration = 25)
        def fitnessFunction(self, pos, pr = 0):
            diff = abs(self.pop.individuals[pos].eval() - pi)
            if pr:
                self.pop.individuals[pos].display()
                print
            return max(pi - diff, 0) 
                
        def isDone(self):
            return abs(self.fitnessFunction(0, 1) - pi) < .001
    share.env = Environment(env)
    share.env.update( {'+1': Operator(lambda obj: obj + 1, 1, "regular"),
                       '1': 1,
                       'e': math.e } )
    gp = PI_GP(100)
    gp.evolve()
    print " -----------------------------------------------------------------"
