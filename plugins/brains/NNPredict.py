# A Neural Network Brain
# D.S. Blank

# Not a true predictor but useful as a platform for testing the new Conx step method.

from pyro.brain import Brain
from pyro.brain.conx import *

class predict(Brain):
   def setup(self):
      """ Create the network. """
      self.sensorCount = self.getRobot().get('range', 'count')
      self.net = Network()
      self.net.addThreeLayers(self.sensorCount + 2, 5, 2)
      #self.net.add(Layer('input', self.sensorCount+2))
      #self.net.addContext(Layer('context', 2), 'hidden')
      #self.net.add(Layer('hidden', 2))
      #self.net.add(Layer('prediction', self.sensorCount))
      #self.net.add(Layer('motorOutput', 2))
      #self.net.connect('input', 'hidden')
      #self.net.connect('context', 'hidden')
      #self.net.connect('hidden', 'prediction')
      #self.net.connect('hidden', 'motorOutput')
      
      self.net.initialize()
      self.net.setVerbosity(0)
      #self.net.setInitContext(0)
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.1)
      self.net.setLearning(1)

      self.trans = 0
      self.rotate = 0
      self.counter = 0
      #self.getRobot().set('range', 'units', 'METERS')
      self.maxvalue = self.getRobot().get('range', 'maxvalue')
      self.new = map(self.scale, self.getRobot().get('range', 'value', 'all'))

   def destroy(self):
      del self.net
      
   def scale(self, val):
      return (val / self.maxvalue)           

   def avoid(self):
      # set targets   
      target_trans  = 1.0
      target_rotate = 0.5
      # left and right and front:
      left = self.getRobot().get('range', 'value', 'front-left', 'minval')
      right = self.getRobot().get('range', 'value', 'front-right', 'minval')
      if left < .5 or right < .5:
         target_trans = 0.5
         target_rotate = 0.0 
      elif left < 0.8:
         target_trans = 0.75
         target_rotate = 0.0
      elif right < 0.8:
         target_trans = 0.75
         target_rotate = 1.0
      return [target_trans, target_rotate]

   def slow(self):
      # set targets   
      target_trans  = 1.0
      target_rotate = 0.5
      # left and right and front:
      left = self.getRobot().get('range', 'value', 'front-left', 'minval')
      right = self.getRobot().get('range', 'value', 'front-right', 'minval')
      if left < .5 or right < .5:
         target_trans = 0.5
      elif left < 0.8:
         target_trans = 0.75
      elif right < 0.8:
         target_trans = 0.75
      return [target_trans, target_rotate]

   def step(self):
      target = self.slow()

      old = self.new + [self.trans, self.rotate] #trans and rotate
      self.new = map(self.scale, self.getRobot().get('range', 'value', 'all'))

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

      self.getRobot().move((self.trans - .5)/2.0, (self.rotate - .5)/2.0)
      self.counter += 1

def INIT(engine):
   return predict('predict', engine)
      
