from pyro.brain import Brain
from pyro.tools import joystick
from time import sleep
import pyro.system.share as share

class JoystickControl(Brain):

   def setup(self):
      self.stick = joystick.Joystick(share.gui)

   def step(self):
      self.getRobot().move( self.stick.translate,
                            self.stick.rotate )

   def destroy(self):
      self.stick.destroy()

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return JoystickControl('JoystickControl', engine)
      
