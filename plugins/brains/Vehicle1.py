"""
Braitenberg Vehicle1 for the Khepera
D.S. Blank
"""

from pyrobot.brain import Brain

class Vehicle(Brain):
   # Only method you have to define for a brain is the step method:

   def setup(self):
      self.maxvalue = self.robot.light[0].getMaxvalue()
   def step(self):
      sensorValue = max([s.distance() for s in self.robot.light[0]["front-all"]]) # front lights
      forward = (self.maxvalue - sensorValue) / self.maxvalue
      self.motors(forward,  forward) # to the left

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   print "OK: robot has light sensors."
   return Vehicle('Braitenberg', engine)
      
