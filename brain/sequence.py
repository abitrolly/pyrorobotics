from pyro.brain.conx import *

net = SRN()
net.addThreeLayers(3,5,1)
net.setAutoSequence(1) # determine sequence from inputs
net.setInputs( [[0, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0]])               
net.setOutputs( [[0, 0], [0, 0.5], [0, 1.0]] )
net.setOrderedInputs(0)
net.setTolerance(.1)
net.setResetEpoch(-1)
net.setEpsilon(0.25)
net.setMomentum(0)
net.setLearnDuringSequence(0)
net.train()
net.setLearning(0)
net.setInteractive(1)
net.sweep()
