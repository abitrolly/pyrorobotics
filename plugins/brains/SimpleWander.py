# A bare brain

from pyro.brain import Brain
from random import random
from time import sleep

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def step(self):
      FTOLERANCE = 35
      LTOLERANCE = 35
      RTOLERANCE = 35

      #left = min(self.getRobot().get('ir', 'value', 0), 
      #           self.getRobot().get('ir', 'value', 1))
      #front = min(self.getRobot().get('ir', 'value', 2), 
      #            self.getRobot().get('ir', 'value', 3))
      #right = min(self.getRobot().get('ir', 'value', 4), 
      #            self.getRobot().get('ir', 'value', 5))

      left = self.getRobot().getSensorGroup('min', 'left')
      right = self.getRobot().getSensorGroup('min', 'right')
      front = self.getRobot().getSensorGroup('min', 'front')
      #left = self.getRobot().getMin('ir', 'range', (0, 1)).distance
      #front = self.getRobot().getMin('ir', 'range', (2, 3)).distance
      #right = self.getRobot().getMin('ir', 'range', (4, 5)).distance

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
            self.getRobot().move(0, .2)
      else:
         self.getRobot().move(.2, 0)

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(robot):
   return SimpleBrain('SimpleBrain', robot)
      
