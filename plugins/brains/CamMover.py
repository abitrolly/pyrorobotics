from pyro.brain import Brain
from pyro.robot.saphira import *
from pyro.brain.fuzzy import *

import time

class SimpleBrain(Brain):
   # Only method you have to define is the step method:
    
   def __init__(self, name, robot):
	Brain.__init__(self, name, robot)

   def step(self):
#	pass
	self.robot.camera.update()
	self.robot.camera.track(cutoff=4.0,mode='yellow')	


# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(robot):
   return SimpleBrain('SimpleBrain', robot)
      
