from pyrobot.brain.conx import *
def prob(v):
    return round(v)
    return int(random.random() < v)
class SigmaNetwork(Network):
    def setup(self):
        self.sumCorrect = 0
    def preSweep(self):
        self.sumCorrect = 0
    def getData(self, i):
        self.propagate(input = self.inputs[i])
        data = {}
        data["input"] = self.inputs[i]
        vector = map(prob, self["output"].activation)
        if round(sum(vector)/float(self["output"].size)) == self.targets[i][0]: # correct guess
            data["output"] = vector
            count = 0
            for i in range(self["output"].size):
                if abs(self["output"].activation[i] - vector[i]) < self.tolerance:
                    count += 1
            if count == self["output"].size:
                self.sumCorrect += 1
        else:
            data["output"] = [(1 - n) for n in vector]
        return data
    def doWhile(self, totalCount, totalCorrect):
        return self.sumCorrect != 4

inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
targets= [[0], [1], [1], [0]]

net = SigmaNetwork()
net.addLayers(2, 5, 21) # make the output as large as you like
net.setInputs( inputs )
net.setTargets( targets)
net.tolerance = 0.4
net.reportRate = 500
net.resetEpoch = 300
net.setEpsilon(0.5)
net.setMomentum(.7)

fp = open("sumXor.dat", "w")
for epsilon in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    for momentum in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        net.setEpsilon(epsilon)
        net.setMomentum(momentum)
        net.initialize()
        net.sumCorrect = 0
        net.train()
        print >> fp, epsilon, momentum, net.epoch - 1
        fp.flush()
fp.close()
