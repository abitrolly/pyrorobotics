# A Neural Network Brain
# D.S. Blank

from pyro.brain import Brain
from pyro.brain.conx import *
from pyro.gui.plot.scatter import *
from pyro.gui.plot.hinton import *

class NNBrain(Brain):
   """
   This is an example brain controlled by a neural network.
   This simple example loads the range sensor data into the
   input layer, and trains the network to stay away from
   things.
   """
   def setup(self):
      """ Init the brain, and create the network. """
      # create the network
      self.net = Network()
      self.net.addThreeLayers(self.robot.get('robot/range/count'), 2, 2)
      self.net.initialize()
      # learning parameters
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.1)
      self.net.setLearning(1)
      # some helpful attributes
      self.counter = 0
      self.doneLearning = 0
      self.maxvalue = self.robot.get('robot/range/maxvalue')
      # visualization
      self.hidScat = Scatter(title = 'Hidden Layer Activations',
                             history = [100, 2, 2], linecount = 3,
                             legend=['Hidden', 'Motor Out', 'Motor Target'])
      self.hidHinton = Hinton(2, title = 'Hidden Layer')
      self.inHinton = Hinton(self.robot.get('robot/range/count'),
                             title = 'Input Layer')
      self.outHinton = Hinton(2, title = 'Output Layer')

   def destroy(self):
      self.hidScat.destroy()
      self.hidHinton.destroy()
      self.outHinton.destroy()
      self.inHinton.destroy()

   def scale(self, val):
      return (val / self.maxvalue)
   
   def step(self):
      if self.doneLearning:
         self.net.setLearning(0)
         self.pleaseStop()
      else:
         self.net.setLearning(1)
         print self.counter,
         
      # first inputs and targets:
      inputs = map(self.scale, self.robot.get('robot/range/all/value'))
      # Compute targets:
      if min(self.robot.get('robot/range/front/value')) < 1:
         target_trans = 0.0
      elif min(self.robot.get('robot/range/back/value')) < 1:
         target_trans = 1.0
      else:
         target_trans = 1.0
      if min(self.robot.get('robot/range/left/value')) < 1:
         target_rotate = 0.0
      elif min(self.robot.get('robot/range/right/value')) < 1:
         target_rotate = 1.0
      else:
         target_rotate = 0.5
      targets = [target_trans, target_rotate]
      # step
      self.net.step(input = inputs, output = targets)
      # print "Learning: trans =", target_trans, "rotate =", target_rotate
      self.hidScat.addPoint( self.net['hidden'].activation[0],
                             self.net['hidden'].activation[1], 0 )
      # get the output, and move:
      trans = (self.net['output'].activation[0] - .5) / 2.0
      rotate = (self.net['output'].activation[1] - .5) / 2.0
      self.hidScat.addPoint( trans * 2 + .5,
                             rotate * 2 + .5, 1)
      self.hidScat.addPoint( target_trans,
                             target_rotate, 2)
      self.inHinton.update(self.net['input'].activation)
      self.hidHinton.update(self.net['hidden'].activation)
      self.outHinton.update(self.net['output'].activation)
      #print "Move    : trans =", trans, "rotate =", rotate
      self.robot.move(trans, rotate)
      self.counter += 1

def INIT(engine):
   return NNBrain('NNBrain', engine)
      
