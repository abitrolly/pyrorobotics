from pyro.brain.conx import SRN

net = SRN()
net.addThreeLayers(1,5,1)
net.setInputs( [[0.0,  0.0,  0.0, 
                 0.5,  0.5,  0.5,
                 0.0,  0.0,  0.0, 
                 0.5,  0.5,  0.5,]] )
net.setOutputs( [[0.0, 0.0,  0.0,
                  0.0, 0.0,  1.0,
                  0.0, 0.0,  0.0,
                  0.0, 0.0,  0.5]] )
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

# 4 step memory test; cannot be learned with no hint (targets = 0)
# but learningDuringSequence = 1
# (or at least it takes longer than 10,000 epochs)
# hints don't help
