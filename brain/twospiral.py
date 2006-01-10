from pyrobot.brain.conx import *
from pyrobot.brain.governor import *

def prob(v):
    return int(random.random() < v)

def test(net, resolution = 30, sum = 1):
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 0
    for x in range(resolution):
        row = ""
        if sum:
            size = 1
        else:
            size = net["output"].size
        for i in range(size):
            for y in range(resolution):
                input = (x/float(resolution), y/float(resolution))
                results = net.propagate(input = input)
                if sum:
                    retval = reduce(operator.add, net["output"].activation) / net["output"].size
                else:
                    retval = results[i]
                c = round(retval, 1)
                if c == 1.0:
                    c = "#"
                else:
                    c = str(c * 10)[0]
                row += "%s" % c
            row += "   "
        print row
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 1

def train(net, sweeps = 30):
    net["candidate"].active = 1
    while not net.complete:
        net.recruitBest()
        net.train(sweeps, cont=1)

fp = open("two-spiral.dat", "r")
inputs = []
targets = []
for line in fp:
    data = map(float, line.split())
    inputs.append( data[:2] )
    targets.append( data[2:] )

inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
targets= [[0], [1], [1], [0]]

## net0 = IncrementalNetwork()
## net0.addLayers(2, 10, 1)
## net0.setInputs( inputs )
## net0.setTargets( targets)
## net0.tolerance = 0.4
## net0.addCandidateLayer(4)
## net0.reportRate = 1
## #net0.train(10)

## net2 = GovernorNetwork(5, 2.1, 0.01, 5, 0.2) # 5, 2.1, 0.3, 5, 0.2
## net2.reportHistograms = 1
## net2.addThreeLayers(2, 10, 1)
## net2.setInputs( inputs )
## net2.setTargets( targets)
## net2.tolerance = 0.4
## net2.reportRate = 1

## #net2.train(10)
## #print net2.ravq

## net3 = Network()
## net3.addLayers(2, 10, 10, 1)
## net3.setInputs( inputs )
## net3.setTargets( targets)
## net3.tolerance = 0.4
## net3.reportRate = 10

class MyNetwork(Network):
    def getData(self, i):
        patterns = {1.0: [1.0, 0.0], 0.0: [0.0, 1.0]}
        data = {}
        data["input"] = self.inputs[i]
        data["output"] = patterns[self.targets[i][0]]
        return data

class MyNetworkSummation(Network):
    def getData(self, i):
        self.propagate(input = self.inputs[i])
        data = {}
        data["input"] = self.inputs[i]
        sum = (reduce(operator.add, self["output"].activation)) / self["output"].size
        if round(sum) == self.targets[i][0]:
            data["output"] = [round(n) for n in self["output"].activation]
        else:
            data["output"] = [round(1 - n) for n in self["output"].activation]
        return data

## net4 = MyNetwork()
## net4.addLayers(2, 10, 10, 2)
## net4.setInputs( inputs )
## net4.setTargets( targets)
## net4.tolerance = 0.4
## net4.reportRate = 10

net5 = MyNetworkSummation()
net5.addLayers(2, 10, 10)
net5.setInputs( inputs )
net5.setTargets( targets)
net5.tolerance = 0.4
net5.reportRate = 1

net = net5

cont = 0
test(net, sum=1)
while not net.complete:
    net.train(50, cont=cont)
    test(net, sum=1)
    cont = 1
