from pyrobot.brain.conx import *

net = IncrementalNetwork("cascade") # "parallel" or "cascade"
net.addLayers(2, 1) # sizes
net.addCandidateLayer(8) # size
net.setInputs( [[0, 0], [0, 1], [1, 0], [1, 1]])
net.setTargets([[0], [1], [1], [0]])
net.tolerance = .1
net.train(100)
sweeps = 300
while not net.complete:
    net.recruitBest()
    net.train(sweeps, cont=1)
net["candidate"].active = 0
net.displayConnections()
net.interactive = 1
net.sweep()
