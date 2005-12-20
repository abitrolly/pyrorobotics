# A Neural Network Brain
# D.S. Blank

from pyrobot.brain import Brain
from pyrobot.brain.conx import *
from pyrobot.gui.plot.scatter import Scatter
import pyrobot.system.share as share

class NNPredict(Brain):
   def setup(self):
      """ Create the network. """
      self.sensorCount = self.robot.range.count
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
      self.maxvalue = self.robot.range.getMaxvalue()
      self.new = [self.scale(s.distance()) for s in self.robot.range["all"]]
      self.plot = Scatter(app=share.gui, linecount=2, connectPoints=0,
                          xEnd=7.0, yEnd=1.2, legend=["Trained", "Test"],
                          title="NN Generalization", width=400)
      self.min = 0.0
      
   def destroy(self):
      self.plot.destroy()
      
   def scale(self, val):
      return (val / self.maxvalue)           

   def avoid(self):
      # set targets   
      target_trans  = 1.0
      target_rotate = 0.5
      # left and right and front:
      self.min = min([s.distance() for s in self.robot.range.span(45, -45)])
      left = min([s.distance() for s in self.robot.range.span(45, -45)])
      right = min([s.distance() for s in self.robot.range.span(45, -45)])
      if left < 1.5 or right < 1.5:
         target_trans = 0.5
      elif left < 3.5 or right < 3.5:
         target_trans = 0.75
      return [target_trans, target_rotate]

   def step(self):
      target = self.avoid()
      old = self.new + [self.trans, self.rotate] #trans and rotate
      self.new = [self.scale(s.distance()) for s in self.robot.range["all"]]
      # results
      if self.net.learning:
         e, c, t, p = self.net.step(input=old, output=target)
         if self.counter % 10 == 0:
            print "error = %.2f" % e
         self.trans, self.rotate = target
      else:
         old = self.new + [self.trans, self.rotate] 
         self.net.step(input=old, output=target)
         self.trans, self.rotate = self.net['output'].activation
         if self.counter % 10 == 0:
            print self.trans, self.rotate
      self.plot.addPoint(self.min, self.trans, not self.net.learning)
      self.robot.move((self.trans - .5)/2.0, (self.rotate - .5)/2.0)
      self.counter += 1

def INIT(engine):
   return NNPredict('NNPredict', engine)
      
