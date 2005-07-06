"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain, avg

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def setup(self):
      self.maxvalue = self.robot.light[0].getMaxvalue()
   def step(self):
      sensorValue = avg([s.distance() for s in self.light[0][2:4]]) # front lights
      forward = (self.maxvalue - sensorValue) / self.maxvalue
      self.motors(forward,  forward) # to the left

def INIT(engine):
   if engine.robot.robot.type != 'K-Team':
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
