from pyro.brain.conx import *
from pyro.brain.governor import *

# goal is to remember first input given in several sequences

#net = SRN()
net = GovernorSRN(1, historySize=5)
net.addThreeLayers(1,5,1)
pause = 15
net.setInputs( [[0.0] + [0.0] * pause + [0.0],
                [0.5] + [0.0] * pause + [0.0],
                [1.0] + [0.0] * pause + [0.0]])               
net.setOutputs( [[0.0] + [0.0] * pause + [0.0],
                 [0.5] + [0.0] * pause + [0.5],
                 [1.0] + [0.0] * pause + [1.0]] )
net.setSequenceType("pattern")
net.setTolerance(.2)
net.setResetEpoch(-1)
net.setEpsilon(0.5) # .25
net.setMomentum(0.0)
net.setLearnDuringSequence(1)
net.decay = 1
net.train()
net.setLearning(0)
net.setInteractive(1)
net.sweep()

# This one can be learned, with learningDuringSequence = 1
# takes about 2100 epochs
