"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyro.brain import Brain

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def step(self):
       lpos, left = self.robot.get('light', 'value', (0, 1, 2), 'min') # light
       rpos, right = self.robot.get('light', 'value', (3, 4, 5), 'min')# light
       forward = .2
       if left < right: # lower means more light
          self.robot.move(forward,  0.3) # to the left
       else:
          self.robot.move(forward, -0.3) # to the right

def INIT(engine):
   if engine.robot.type != 'khepera':
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
