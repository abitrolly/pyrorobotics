#Define ArmorRobot, an interface to the
#pair of arms

from pyro.robot import *

class ArmorRobot(Robot):
   def __init__(self, name = None, simiulator = 1):
      Robot.__init__(self, name, "Armor")

   def _draw(self, options, renderer):
      renderer.xformPush()
      rederer.color(.5, .5, .5)

      renderer.box((0, 0, 0), \
                   (1, 0, 0), \
                   (1, 1, 0), \
                   (1, 1, 1))

      renderer.xformPop()

   def getOptions(self):
      pass

   def connect(self):
      pass

   def localize(self, x = 0.0, y = 0.0, z = 0.0):
      pass

   def disconnect(self):
      pass

   def loadDrivers(self):
      pass

   def update(self):
      pass
   

       
