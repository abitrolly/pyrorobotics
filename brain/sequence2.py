from pyro.brain.conx import Network
from pyro.brain.governor import *
import Numeric

class myGovernorSRN(GovernorSRN):
    def getInput(self, pos, start = 0):
        retval = {}
        if pos >= len(self.inputs):
            raise IndexError, ('getInput() pattern beyond range.', pos)
        if self.verbosity > 0: print "Getting input", pos, "..."
        if len(self.inputMap) == 0:
            name = self.layers[0].name
            retval[name] = self.inputs[pos][start:start+self[name].size]
        else: # mapInput set manually
            for vals in self.inputMap:
                (v1, offset) = vals
                retval[v1]= self.inputs[pos][offset:offset+self[v1].size]
        return retval
    def getTarget(self, pos, start = 0):
        retval = {}
        if pos >= len(self.targets):
            return  retval # there may be no target 
        if self.verbosity > 1: print "Getting target", pos, "..."
        if len(self.targetMap) == 0:
            name = self.layers[len(self.layers)-1].name
            retval[name] = self.targets[pos][start:start+self[name].size]
        else: # set manually
            for vals in self.targetMap:
                (v1, offset) = vals
                retval[v1] = self.targets[pos][offset:offset+self[v1].size]
        return retval
    def change_weights(self):
        Network.change_weights(self)
        if net.useRAVQ:
            # put it back the way that it was
            self.copyActivations(self["input"], self.lastInput)
            # copy context
            self.copyActivations(self["context"], self.lastContext)
            self.propagate()
            self.copyHiddenToContext()
    def preprop(self, pattern, step):
        """
        Extends preprop() by adding support for clearing context layers
        and predicting.
        """
        if self.sequenceLength > 1:
            if step == 0 and self.initContext:
                self.clearContext()
        else: # if seq length is one, you better be doing ordered
            if pattern == 0 and self.initContext:
                self.clearContext()
        # --------------------------------------------------------------------------------------
        if self.useRAVQ:
            # get what the input would be:
            input = self.getInput(pattern, step)
            target = self.getTarget(pattern, step)
            if self.count == 0:
                self.clearContext()
            # make copy
            self.lastInput = input["input"]
            self.lastContext = self["context"].activation
            # get the sizes:
            inputSize   = self["input"].size
            contextSize = self["context"].size
            # map it in the RAVQ:
            index, modelVector = net.map(input["input"] + list(self["context"].activation) + target["output"])
            array = net.nextItem()
            # stick it in the network
            if self.verbosity > 0:
                print "RAVQ input:", input["input"] + list(self["context"].activation) + target["output"]
                print "RAVQ MV:", modelVector
                print "RAVQ array:", array
            if index == -1: # no winner
                self.copyActivations(self["input"], input["input"])
                self.copyTargets(self["output"], target["output"])
            else:
                self.copyActivations(self["input"], array[0:inputSize])
                self.copyActivations(self["context"], array[inputSize:inputSize+contextSize])
                self.copyTargets(self["output"], array[inputSize+contextSize:])                
        else:
            # this loads inputs into the network:
            Network.preprop(self, pattern, step) # must go here, consider raam example
        # --------------------------------------------------------------------------------------
        for p in self.prediction:
            if self.useRAVQ:
                raise AttributeError, "Governed network doesn't work with prediction"
            (inName, outName) = p
            inLayer = self.getLayer(inName)
            if not inLayer.type == 'Input':
                raise LayerError, ('Prediction input layer not type \'Input\'.', inLayer.type)
            outLayer = self.getLayer(outName)
            if not outLayer.type == 'Output':
                raise LayerError, ('Prediction output layer not type \'Output\'.', outLayer.type)
            if self.sequenceLength == 1:
                position = (pattern + 1) % len(self.inputs)
                outLayer.copyTargets(self.inputs[position])
            else:
                start = ((step + 1) * inLayer.size) % len(self.replacePatterns(self.inputs[pattern]))
                self.copyTargets(outLayer, self.inputs[pattern], start)
# set RAVQ parameters
ravqBuffer = 5 # old params (4, 2.1, 1.1, 2, .2)
govEpsilon = 2.1  
delta = 0.00
govBuffer = 2
alpha = 0.2
net = myGovernorSRN(ravqBuffer, govEpsilon, delta, govBuffer, alpha, mask = [5, 1, 1, 1, 1, 1, 5])
net.useRAVQ = 1
net.addThreeLayers(1,5,1)
net.setInputs( [[0.0,  0.0,  0.0, 
                 0.5,  0.5,  0.5,
                 0.0,  0.0,  0.0, 
                 0.5,  0.5,  0.5]] )
net.setOutputs( [[0.0, 0.0,  0.0,
                  0.0, 0.0,  1.0,
                  0.0, 0.0,  0.0,
                  0.0, 0.0,  0.5]] )
net.setLayerVerification(0)
net.setOrderedInputs(0)
net.setTolerance(-.1)
net.setResetEpoch(30)
net.setResetLimit(1)
net.setEpsilon(0.25)
net.setMomentum(0)
net.setLearnDuringSequence(1)
net.train()
print net.ravq
net.useRAVQ = 0
net.setLearning(0)
net.setInteractive(1)
net.sweep()

# preprop        - get intended input/target, map RAVQ/get array as input/context/target
# propagate      - propagate
#     clearcontext
# backprop       - compute wed/bed
#    copyContext - copy hidden->context
# update_weights - change weights, but back, propagate, copycontext
