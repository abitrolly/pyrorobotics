# A Neural Network Brain
# D.S. Blank

from pyro.brain import Brain
from pyro.brain.conx import *

class predict(Brain):
   def setup(self):
      """ Create the network. """
      self.sensorCount = self.get('robot', 'range', 'count')
      self.net = Network()
      self.net.addThreeLayers(self.sensorCount + 2, 5, 2)
      self.net.initialize()
      self.net.setVerbosity(0)
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.1)
      self.net.setLearning(1)
      self.trans = 0
      self.rotate = 0
      self.counter = 0
      self.maxvalue = self.get('robot', 'range', 'maxvalue')
      self.new = map(self.scale, self.get('robot', 'range', 'all', 'value'))

   def destroy(self):
      del self.net
      
   def scale(self, val):
      return (val / self.maxvalue)           

   def avoid(self):
      # set targets   
      target_trans  = 1.0
      target_rotate = 0.5
      # left and right and front:
      left = min(self.get('robot', 'range', 'front-left', 'value'))
      right = min(self.get('robot', 'range', 'front-right', 'value'))
      if left < 1.5 or right < 1.5:
         target_trans = 0.5
      elif left < 1.8:
         target_trans = 0.75
      elif right < 1.8:
         target_trans = 0.75
      return [target_trans, target_rotate]

   def step(self):
      target = self.avoid()

      old = self.new + [self.trans, self.rotate] #trans and rotate
      self.new = map(self.scale, self.get('robot', 'range', 'all', 'value'))

      # results
      if self.net.learning:
         e, c, t = self.net.step(input=old, output=target)
         if self.counter % 10 == 0:
            print "error = %.2f" % e
         self.trans, self.rotate = target
      else:
         old = self.new + [self.trans, self.rotate] 
         self.net.step(input=old, output=target)
         self.trans, self.rotate = self.net.getLayer('output').getActivations()
         if self.counter % 10 == 0:
            print self.trans, self.rotate

      self.robot.move((self.trans - .5)/2.0, (self.rotate - .5)/2.0)
      self.counter += 1

def INIT(engine):
   return predict('predict', engine)
      
