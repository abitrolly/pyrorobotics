from pyro.brain.conx import *

# goal is to remember first input given in several sequences

net = SRN()
net.addThreeLayers(1,5,1)
net.setInputs( [[0.0, 0.0],
                [0.5, 0.0],
                [1.0, 0.0]])               
net.setOutputs( [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0]] )
net.setOrderedInputs(0)
net.setTolerance(.1)
net.setResetEpoch(-1)
net.setEpsilon(0.25)
net.setMomentum(0)
net.setLearnDuringSequence(1)
net.train()
net.setLearning(0)
net.setInteractive(1)
net.sweep()

# A single pause.
# This one can be learned, with learningDuringSequence = 1
# takes about 2100 epochs
