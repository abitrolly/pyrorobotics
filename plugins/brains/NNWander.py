# A Neural Network Brain
# D.S. Blank

from pyro.brain import Brain
from pyro.brain.conx import *

class NNBrain(Brain):
   """
   This is an example brain controlled by a neural network.
   This simple example loads the range sensor data into the
   input layer, and trains the network to stay away from
   things.
   """
   def __init__(self, name, robot):
      """ Init the brain, and create the network. """
      Brain.__init__(self, name, robot)
      self.net = Network()
      self.net.addThreeLayers(self.getRobot().get('range', 'count'), 5, 2)
      self.net.setBatch(0)
      self.net.initialize()
      self.net.setQuickProp(0)
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.975)
      self.maxvalue = self.getRobot().get('range', 'maxvalue')

   def scale(val):
      return (val / self.maxvalue)
   
   def step(self):
      # First, set inputs and targets:
      ins = map(self.scale, self.getRobot().get('range', 'all'))
      self.net.setInputs([ ins ])
      # Compute targets:
      #print "Front:", self.getRobot().getSensorGroup('min', 'front')[1]
      #print "Back:", self.getRobot().getSensorGroup('min', 'back')[1]
      #print "Left:", self.getRobot().getSensorGroup('min', 'left')[1]
      #print "Right:", self.getRobot().getSensorGroup('min', 'right')[1]
      if self.getRobot().getSensorGroup('min', 'front')[1] < 1:
         target_trans = 0.0
      elif self.getRobot().getSensorGroup('min', 'back')[1] < 1:
         target_trans = 1.0
      else:
         target_trans = 1.0
      if self.getRobot().getSensorGroup('min', 'left')[1] < 1:
         target_rotate = 0.0
      elif self.getRobot().getSensorGroup('min', 'right')[1] < 1:
         target_rotate = 1.0
      else:
         target_rotate = 0.5
      self.net.setOutputs([[target_trans, target_rotate]])
      # next, cycle through inputs/outputs:
      #print "Learning: trans =", target_trans, "rotate =", target_rotate
      self.net.sweep()
      # get the output, and move:
      trans = (self.net.getLayer('output').activation[0] - .5) / 2.0
      rotate = (self.net.getLayer('output').activation[1] - .5) / 2.0
      #print "Move    : trans =", trans, "rotate =", rotate
      self.getRobot().move(trans, rotate)

def INIT(robot):
   return NNBrain('NNBrain', robot)
      
