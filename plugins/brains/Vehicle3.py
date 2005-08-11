"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain

class Vehicle(Brain):
   def setup(self):
      self.forwardAmount = 0.2
      self.turnAmount    = 0.3

   def step(self):
      left = min([s.distance() for s in self.robot.light[0]["front-left"]])
      right = min([s.distance() for s in self.robot.light[0]["front-right"]])
      if left > right: # lower means less light
         self.move(self.forwardAmount,  self.turnAmount)
      else:
         self.move(self.forwardAmount, -self.turnAmount)

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
