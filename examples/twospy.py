# to turn off psyco uncomment these:
#import pyrobot.system.share
#pyrobot.system.share.debug = 1

from pyrobot.brain.conx import *
from pyrobot.brain.cascor import *

def oneTrial():
    n = CascadeCorNet(2,1, patience = 12, maxOutputEpochs = 200, maxCandEpochs = 200)
    n.addCandidateLayer(8)
    n.setInputs(inputs)
    n.setTargets(targets)
    n.tolerance = 0.4
    #n.epsilon = 1.0
    print n.outputEpsilon
    print n.outputMu
    n.train(40)

def mean(seq):
    return Numeric.sum(seq)/float(len(seq))

def center(seq):
    return seq - mean(seq)

def compare():
    n = CascadeCorNet(2,1, patience = 12, maxOutputEpochs = 200, maxCandEpochs = 200)
    #n = CascadeCorNet(2,1, patience = 50, maxOutputEpochs = 200, maxCandEpochs = 200)
    n.maxRandom = 1.0
    #n.addCandidateLayer(1) #for debugging
    n.addCandidateLayer(8)
    n.useFahlmanActivationFunction()
    #n["output"].weight = Numeric.array([0.4920000])
    #n["input","output"].weight = Numeric.array([[0.9700000],[-0.664]])
    lines = open("twospiral.dat",'r').readlines()
    inputs = [[float(num) for num in line.split()[:-1]] for line in lines]
    inputs = Numeric.array(inputs)
    targets = Numeric.array([[float(line.split()[-1])] for line in lines])
    n.setInputs(inputs)
    n.setTargets(targets)
    n.tolerance = 0.4
    n.outputEpsilon = 1.0/194.0
    n.outputDecay = 0.0
    n.candEpsilon = 100.0/194.0
    n.candDecay = 0.0
    n.candChangeThreshold = 0.03
    #n.candChangeThreshold = 0.025
    n.outputChangeThreshold = 0.01
    n.setSigmoid_prime_offset( 0.1)
    n.outputMu = 2.0
    n.candMu = 2.0
    import pdb
    #pdb.set_trace()
    #n.switchToOutputParams()
    #n.trainOutputs(200)
    n.setOrderedInputs(1)
    print n .sigmoid_prime_offset
    #pdb.set_trace()
    n.train(50)
    print n["input"].weight
    print n["input","output"].weight
    print n["output"].weight
def compare2():
    n = CascadeCorNet(2,1, patience = 12, maxOutputEpochs = 200, maxCandEpochs = 200)
    #n = CascadeCorNet(2,1, patience = 50, maxOutputEpochs = 200, maxCandEpochs = 200)
    n.maxRandom = 1.0
    n.addCandidateLayer(1)
    n.useFahlmanActivationFunction()
    n["output"].weight = Numeric.array([0.4920000])
    n["input","output"].weight = Numeric.array([[0.9700000],[-0.664]])
    lines = open("test.data",'r').readlines()
    inputs = [[float(num) for num in line.split()[:-1]] for line in lines]
    inputs = Numeric.array(inputs)
    targets = Numeric.array([[float(line.split()[-1])] for line in lines])
    n.setInputs(inputs)
    n.setTargets(targets)
    n.tolerance = 0.4
    n.outputEpsilon = 1.0/5.0
    n.outputDecay = 0.0
    #n.candEpsilon = 100.0/5.0
    n.candEpsilon = 15.0/50.0
    n.candDecay = 0.0
    n.candChangeThreshold = 0.03
    n.outputChangeThreshold = 0.01
    n.setSigmoid_prime_offset( 0.1)
    n.outputMu = 2.0
    n.candMu = 2.0
    import pdb
    
    #n.switchToOutputParams()
    #n.trainOutputs(200)
    n.setOrderedInputs(1)
    print n .sigmoid_prime_offset
    #pdb.set_trace()
    n.train(50)
    print n["input"].weight
    print n["input","output"].weight
    print n["output"].weight
    
if __name__=="__main__":
    compare()
    #compare2()
    import sys
    sys.exit()

    lines = open("twospiral.txt",'r').readlines()
    #lines = open("twospiral.dat",'r').readlines()
    inputs = [[float(num) for num in line.split()[:-1]] for line in lines]
    inputs = Numeric.array(inputs)
    targets = Numeric.array([[float(line.split()[-1])] for line in lines])

    #inputs = Numeric.array([[float(num)  for num in line.split()[:-1]] for line in lines])
    #targets = Numeric.array([[float(line.split()[-1]) + 0.5] for line in lines])

   ##  #prepare for new activation function
##     intputs = center(inputs)*2.0
##     targets = center([datum*2 for datum in targets])
    
    print targets
    print "max", max(targets)
    print "min", min(targets)
    
    n = CascadeCorNet(2,1, patience = 12, maxOutputEpochs = 200, maxCandEpochs = 200)
    
    
    n.addCandidateLayer(16)
    #change activation function
    #n.useFahlmanActivationFunction()
    #n.useTanhActivationFunction()
    n["input","output"].weight = Numeric.array([[random.gauss(0,0.5)],[random.gauss(0,0.5)]])
    n["input"].weight = Numeric.array([random.gauss(0,0.5),random.gauss(0,0.5)])
    print n["input"].weight
    print n["input","output"].weight
    n.setInputs(inputs)
    n.setTargets(targets)

    n.tolerance = 0.4
    n.outputEpsilon = 1.0
    n.candEpsilon = 100.0/194.0
    n.candChangeThreshold = 0.03
    n.outputChangeThreshold = 0.005
    n.outputMu = 2.25#2.0
    #n.candMu = 2.0
    #n.sigmoid_prime_offset =  0.001
    #n.outputDecay = 0.0#-0.01
    #n.candDecay = 0.0#-0.01
    print n.candChangeThreshold
    print n.outputEpsilon
    print n.candEpsilon
    print n.outputChangeThreshold
    n.train(20)
    print n.candEpsilon
    print n.outputEpsilon
    print n.candChangeThreshold
    print n.outputChangeThreshold
##     for i in range(100):
##         print "Trial ",i,"\n\n\n"
##         oneTrial()
