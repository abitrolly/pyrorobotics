""" A Governor Self-regulating Network

Designed to give the power of offline learning to online learning

"""

from pyro.brain.VisConx.VisRobotConx import *
from pyro.brain.conx import *
from pyro.brain.psom.vis import *
from pyro.brain.ravq import *


class Governor(Network, VisPsom):
    """ A Neural Network Class with SOM Regulator. """

    def __init__(self, inputSize, hiddenSize, outputSize):
        """ Constructor for Governor Class """
        Network.__init__(self, "Governor Network")
        VisPsom.__init__(self, xdim = 1, ydim = 3, dim = inputSize + outputSize)
        self.addThreeLayers( inputSize, hiddenSize, outputSize)

    def train(self):
        """ Overload network train to sample first with SOM, then train"""
        # train som on input + target pair
        dim = self.getLayer("input").size + self.getLayer("output").size
        dset = dataset(dim = dim )
        # init_vector = vector([.0] * dim), dim = dim )
        for i in range( len( self.inputs) ):
            dset.addvec( vector(self.inputs[i] + self.targets[i]) )
        dset.display()
        self.init_training(0.02, 1.0, 5000) #len(self.inputs))
        print "Training SOM..."
        self.train_from_dataset( dset, mode = 'rand' )
        # test: just train on the model vectors:
        ins = [ ]
        outs = [ ]
        for x in range(self.xdim):
            for y in range(self.ydim):
                modelvector = self.get_model_vector(point(x = x, y = y))
                #ins.append( map(round, modelvector[0:self.getLayer("input").size] ))
                ins.append( modelvector[0:self.getLayer("input").size] )
                #outs.append( map(round, modelvector[self.getLayer("output").size:] ))
                outs.append( modelvector[self.getLayer("output").size:] )
        print "ins :", ins
        print "outs:", outs
        self.setInputs( ins )
        self.setTargets( outs)
        print "Training Network..."
        Network.train(self)

class RAVQGovernor:
    def __init__(self, network, ravq, threshold):
        self.net = network
        self.ravq = ravq
        self.threshold = threshold
    def setLearning(self):
        count = self.ravq.getWinnerCount()
        if count > self.threshold:
            return 0
        else:
            return 1
    def setEpsilon(self):
        return self.net.epsilon
    def step(self, inputs, targets):
        self.ravq.input(inputs + targets)
        self.net.setLearning(self.setLearning())
        self.net.setEpsilon(self.setEpsilon())
        return self.net.step(input = inputs, output = targets)
        
        
if __name__ == '__main__':
    rnet = Governor(4, 2, 4)
    rnet.setInputs([[1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],
                    [1, 0, 0, 0],

                    [0, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 0, 0],

                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                    ])

    rnet.setTargets([[1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     [1, 0, 0, 0],
                     
                     [0, 1, 0, 0],
                     [0, 1, 0, 0],
                     [0, 1, 0, 0],
                     [0, 1, 0, 0],
                     [0, 1, 0, 0],
                     
                     [0, 0, 1, 0],
                     [0, 0, 0, 1],
                     ])
    rnet.setTolerance(.2)
    # do/don't do:
    rnet.train()
    rnet.setInputs([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                    ])
    rnet.setTargets([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1],
                     ])
    #Network.train(rnet)
    rnet.setLearning(0)
    rnet.setInteractive(1)
    rnet.sweep()

    
    
