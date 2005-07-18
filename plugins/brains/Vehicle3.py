"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def step(self):
      left = min([s.distance() for s in self.robot.light[0]["front-left"]])
      right = min([s.distance() for s in self.robot.light[0]["front-right"]])
      forward = .2
      if left < right: # lower means more light
         self.move(forward,  0.3) # to the left
      else:
         self.move(forward, -0.3) # to the right

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
