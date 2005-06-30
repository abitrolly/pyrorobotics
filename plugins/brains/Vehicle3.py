"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def step(self):
      left = min([s.distance() for s in self.robot.light[0][0:3]])
      right = min([s.distance() for s in self.robot.light[0][3:6]])
      forward = .2
      if left < right: # lower means more light
         self.move(forward,  0.3) # to the left
      else:
         self.move(forward, -0.3) # to the right

def INIT(engine):
   if engine.robot.type != 'K-Team':
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
