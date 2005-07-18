"""
Braitenberg Vehicle2a for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain, avg

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def setup(self):
      self.robot.light[0].units = "SCALED"

   def step(self):
      leftSpeed  = self.robot.light[0]["left"][0].value # left lights
      rightSpeed = self.robot.light[0]["right"][0].value # right lights
      self.motors(leftSpeed,  rightSpeed) # to the left

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg2a', engine)
      
