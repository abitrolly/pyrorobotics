# --------------------------------------------------------
# A Braitenberg Vehicle
# D.S. Blank
# --------------------------------------------------------

# import some additional libraries:

from pyro.brain import Brain
from math import fabs

# subclass brain:

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:
   def setup(self):
      self.getRobot().set('light', 'units', 'SCALED')

   def step(self):
       left = self.robot.get('light', 1)  # Khepera specific
       right = self.robot.get('light', 4) # Khepera specific

       print "Right:", right, "Left:", left

       turn = (right - left) / self.robot.getMax('light').distance
       forward = .3 - fabs(turn * .3) # go when no light

       self.robot.move(forward, turn)

# The function INIT that takes a robot and returns a brain:

def INIT(engine):
   if engine.robot.type != 'khepera':
      raise "Robot should be a Khepera"
   return Vehicle('Braitenberg', engine)
      
