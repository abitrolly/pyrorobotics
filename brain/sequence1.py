from pyro.brain.governor import GovernorSRN

mask = [0] * 4 + [1] * 5 + [2] * 4
net = GovernorSRN(delta = 0.0, epsilon = 2.1, historySize = 5, mask = mask)
net.addThreeLayers(4,5,4)
net.setPatterns({"a" : [1,0,0,0],
                 "b" : [0,1,0,0],
                 "c" : [0,0,1,0],
                 "d" : [0,0,0,1]})
#net.setInputs( [["a", "a", "a", "b", "b", "b", "a", "a", "d", "b",
#                 "a", "a", "a", "c", "c", "c", "a", "a", "d", "c"]] )
net.setInputs( [["a", "b", "a", "d", "b",
                 "a", "c", "a", "d", "c"]] )
net.predict("input", "output")
net.setOrderedInputs(0)
net.setTolerance(.3)
net.setResetEpoch(50)
net.setResetLimit(1)
net.setEpsilon(0.25)
net.setMomentum(0)
net.setLearnDuringSequence(1)
net.governing = 1
net.train()
print net.ravq
net.setLearning(0)
net.setInteractive(1)
net.sweep()

# 4 step memory test; cannot be learned with no hint (targets = 0)
# but learningDuringSequence = 1
# (or at least it takes longer than 10,000 epochs)
# hints don't help
