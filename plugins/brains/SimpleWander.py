# A bare brain

from pyro.brain import Brain
from random import random
from time import sleep

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def step(self):
      FTOLERANCE = 1.0
      LTOLERANCE = 1.0
      RTOLERANCE = 1.0

      left = self.getRobot().get('range', 'value', 'left', 'min')[1]
      right = self.getRobot().get('range', 'value', 'right', 'min')[1]
      front = self.getRobot().get('range', 'value', 'front', 'min')[1]

      print "left", left, "front", front, "right", right

      if (left < LTOLERANCE and right < RTOLERANCE):
         self.getRobot().move(0, .2)
         #sleep(.5)
      elif (right < RTOLERANCE):
         self.getRobot().move(0, .2)
      elif (left < LTOLERANCE):
         self.getRobot().move(0, -.2)
      elif (front < FTOLERANCE):
         if random() < .5:
            self.getRobot().move(0, .2)
         else:
            self.getRobot().move(0, -.2)
      else:
         self.getRobot().move(.2, 0)

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
