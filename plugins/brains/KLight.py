# --------------------------------------------------------
# A Braitenberg Vehicle
# D.S. Blank
# --------------------------------------------------------

# import some additional libraries:

from pyrobot.brain import Brain
from math import fabs

# subclass brain:

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:
   def setup(self):
      self.set('/robot/light/units', 'SCALED')

   def step(self):
       left = self.get('/robot/light/1/value')  # Khepera specific
       right = self.get('/robot/light/4/value') # Khepera specific

       print "Right:", right, "Left:", left

       turn = (right - left) / max(self.get('/robot/light/all/value'))
       forward = .3 - fabs(turn * .3) # go when no light

       self.robot.move(forward, turn)

# The function INIT that takes a robot and returns a brain:

def INIT(engine):
   if engine.robot.get('/robot/type') != 'khepera':
      raise "Robot should be a Khepera"
   return Vehicle('Braitenberg', engine)
      
