# A bare brain

from pyro.brain import Brain
from pyro.tools import joystick
from time import sleep

class DirectControl(Brain):

   def setup(self, **args):
      self.stick = joystick.Joystick(self.robot)
      # initialize your vars here!
      
   # Only method you have to define is the step method:

   def step(self):
      pass
      #self.quit()

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return DirectControl('DirectControl', engine, my_arg = "testing")
      
