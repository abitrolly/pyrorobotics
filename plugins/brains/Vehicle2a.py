"""
Braitenberg Vehicle2a for the Khepera
D.S. Blank
"""

from pyro.brain import Brain, avg

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def setup(self):
      self.set('/devices/light0/units', "RAW")
      self.maxvalue = self.get('/devices/light0/maxvalue')

   def convert(self, raw):
      return (self.maxvalue - raw) / self.maxvalue
      
   def step(self):
      leftSensorValue  = self.get('/devices/light0/1/value') # left lights
      rightSensorValue = self.get('/devices/light0/4/value') # right lights
      leftSpeed  = self.convert(leftSensorValue)
      rightSpeed = self.convert(rightSensorValue)
      self.robot.motors(leftSpeed,  rightSpeed) # to the left

def INIT(engine):
   if engine.robot.get("robot/type") != 'K-Team':
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg2a', engine)
      
