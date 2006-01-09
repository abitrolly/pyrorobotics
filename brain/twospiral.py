from pyrobot.brain.conx import *
from pyrobot.brain.governor import *

def test(net, resolution = 30):
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 0
    for x in range(resolution):
        row = ""
        for y in range(resolution):
            input = (x/float(resolution), y/float(resolution))
            results = net.propagate(input = input)
            row += "%d" % int(round(results[0]))
        print row
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 1

fp = open("two-spiral.dat", "r")
inputs = []
targets = []
for line in fp:
    data = map(float, line.split())
    inputs.append( data[:2] )
    targets.append( data[2:] )

net = IncrementalNetwork()
net.addLayers(2, 10, 1)
net.setInputs( inputs )
net.setTargets( targets)
net.tolerance = 0.4
net.addCandidateLayer(4)
net.reportRate = 1
#net.train(10)

net2 = GovernorNetwork()
net2.addThreeLayers(2, 10, 1)
net2.setInputs( inputs )
net2.setTargets( targets)
net2.tolerance = 0.4
net2.reportRate = 1

def train(net, sweeps = 30):
    net["candidate"].active = 1
    while not net.complete:
        net.recruitBest()
        net.train(sweeps, cont=1)
