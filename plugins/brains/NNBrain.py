# NNBrain.py
from pyrobot.brain import Brain
from pyrobot.brain.conx import SRN

class NNBrain(Brain):
    def setup(self):
        self.robot.range.units = "scaled"
        self.net = SRN()
        self.sequenceType = "ordered-continuous"
        # INPUT: ir, ears, mouth[t-1]
        self.net.addLayer("input", len(self.robot.range) + 4 + 1) # sonar, ears, speech[t-1]
        self.net.addContextLayer("context", 2, "hidden")
        self.net.addLayer("hidden", 2)
        # OUTPUT: trans, rotate, say
        self.net.addLayer("output", 3)
        # ----------------------------------
        self.net.connect("input", "output")
        self.net.connect("context", "hidden")
        self.net.connect("hidden", "output")
        self.net["context"].setActivations(.5)
        self.net.learning = 0
        self.net.setLayerVerification(0)

    def step(self):
        inputs = self.robot.range.distance() + ([0] * 4) + [self.net["output"].activation[2]]
        self.net.propagate(input=inputs)
        outputActivations = self.net["output"].activation[:]
        t, r = [((v * 2) - 1) for v in outputActivations[:2]]
        self.robot.move(t, r)
        
    def propagate(self, inputs):
        self.net.propagate(input=inputs)
        #t, r = [((v * 2) - 1) for v in outputActivations]
        return self.net["output"].activation[:]

def INIT(eng):
    return NNBrain(engine=eng)
