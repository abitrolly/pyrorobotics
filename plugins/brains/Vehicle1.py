"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain, avg

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def setup(self):
      self.set('/devices/light0/units', "RAW")
      self.maxvalue = self.get('/devices/light0/maxvalue')
   def step(self):
      sensorValue = avg(self.get('/devices/light0/2,3/value')) # front lights
      forward = (self.maxvalue - sensorValue) / self.maxvalue
      self.motors(forward,  forward) # to the left

def INIT(engine):
   if engine.robot.get("robot/type") != 'K-Team':
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
