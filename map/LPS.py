# Local Perceptual Space

from pyro.brain import Brain
from pyro.gui.plot.matrix import Matrix
from pyro.map.lps import LPS
from math import sqrt

class LPSBrain(Brain):

   def setup(self):
      self.lps = LPS( 20, 20 )

   def step(self):
      robot = self.getRobot()
      self.lps.reset() # reset counts
      self.lps.plotSensor(robot, 'sonar')
      self.lps.redraw()

def INIT(engine):
   return LPSBrain('LPSBrain', engine)
      
