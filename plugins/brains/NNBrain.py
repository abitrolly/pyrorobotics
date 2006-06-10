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

    def step(self, ot1, or1):
        t, r = [((v * 2) - 1) for v in [ot1, or1]]
        self.robot.move(t, r)
        
    def propagate(self, sounds):
        inputs = self.robot.range.distance() + sounds + [self.net["output"].activation[2]]
        self.net.propagate(input=inputs)
        self.net.copyHiddenToContext()
        return [v for v in self.net["output"].activation] # t, r, speech

def INIT(eng):
    return NNBrain(engine=eng)
