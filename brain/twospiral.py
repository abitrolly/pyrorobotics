from pyrobot.brain.conx import *
from pyrobot.brain.governor import *

def test(net, resolution = 30):
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 0
    for x in range(resolution):
        row = ""
        for i in range(net["output"].size):
            for y in range(resolution):
                input = (x/float(resolution), y/float(resolution))
                results = net.propagate(input = input)
                c = round(results[i], 1)
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

net0 = IncrementalNetwork()
net0.addLayers(2, 10, 1)
net0.setInputs( inputs )
net0.setTargets( targets)
net0.tolerance = 0.4
net0.addCandidateLayer(4)
net0.reportRate = 1
#net0.train(10)

net2 = GovernorNetwork(5, 2.1, 0.01, 5, 0.2) # 5, 2.1, 0.3, 5, 0.2
net2.reportHistograms = 1
net2.addThreeLayers(2, 10, 1)
net2.setInputs( inputs )
net2.setTargets( targets)
net2.tolerance = 0.4
net2.reportRate = 1

#net2.train(10)
#print net2.ravq

net3 = Network()
net3.addLayers(2, 10, 10, 1)
net3.setInputs( inputs )
net3.setTargets( targets)
net3.tolerance = 0.4
net3.reportRate = 10

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
        sum = reduce(operator.add, self["output"].activation) / self["output"].size
        if abs(sum - self.targets[i]) < self.tolerance:
            data["output"] = [n for n in self["output"].activation]
        else:
            data["output"] = [1 - n for n in self["output"].activation]
        return data

net4 = MyNetwork()
net4.addLayers(2, 10, 10, 2)
net4.setInputs( inputs )
net4.setTargets( targets)
net4.tolerance = 0.4
net4.reportRate = 10

net = net4

cont = 0
while not net.complete:
    net.train(50, cont=cont)
    test(net)
    cont = 1
