"""
A Braitenberg Vehicle for the Khepera
D.S. Blank
"""

# import some additional libraries:

from pyrobot.brain import Brain
from math import fabs

# subclass brain:

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def step(self):
       left = self.robot.light[0][1].distance()  # Khepera specific
       right = self.robot.light[0][4].distance() # Khepera specific

       turn = (right - left) / max([s.distance() for s in self.robot.light[0]["all"]])
       forward = .3 - fabs(turn * .3) # go when no light

       self.move(forward, turn)

# The function INIT that takes a robot and returns a brain:

def INIT(engine):
   if engine.robot.robot.type != 'khepera':
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
