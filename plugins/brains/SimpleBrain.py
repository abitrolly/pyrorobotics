# A bare brain

from pyro.brain import Brain

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def step(self):
      self.getRobot().move(.3, .2)
      #self.quit()

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
