from pyrobot.brain.conx import *

net = IncrementalNetwork()
net.addLayers(2, 1)
net.addCandidateLayer(1)
net.setInputs( [[0, 0], [0, 1], [1, 0], [1, 1]])
net.setTargets([[0], [1], [1], [0]])
net.tolerance = .1
