"""
Braitenberg Vehicle3b
The more light sensed on the left side the slower the right motor moves.
The more light sensed on the right side the slower the left motor moves.
This causes the robot to slow and turn away from a light source and then
speed away from it.  
"""

from pyrobot.brain import Brain

class Vehicle(Brain):
   def setup(self):
      self.robot.light[0].units = "SCALED"
   def step(self):
      leftSpeed = 1.0 - self.robot.light[0]["right"][0].value
      rightSpeed = 1.0 - self.robot.light[0]["left"][0].value
      print "leftSpeed, rightSpeed:", leftSpeed, rightSpeed
      self.motors(leftSpeed,  rightSpeed) 

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   return Vehicle('Braitenberg', engine)
      
