# A bare brain

from pyro.brain import Brain
from random import random
from time import sleep
from pyro.map.lps import LPS

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def setup(self):
      self.lps = LPS( 20, 20 ) # create the Local Perceptiual Space window

   def step(self):
      robot = self.getRobot()
      self.lps.reset() # reset counts
      self.lps.plotSensor(robot, 'sonar')
      self.lps.redraw()

      FTOLERANCE = 1.0
      LTOLERANCE = 1.0
      RTOLERANCE = 1.0

      left = robot.get('range', 'value', 'left', 'min')[1]
      right = robot.get('range', 'value', 'right', 'min')[1]
      front = robot.get('range', 'value', 'front', 'min')[1]

      print "left", left, "front", front, "right", right

      if (left < LTOLERANCE and right < RTOLERANCE):
         robot.move(0, .2)
         #sleep(.5)
      elif (right < RTOLERANCE):
         robot.move(0, .2)
      elif (left < LTOLERANCE):
         robot.move(0, -.2)
      elif (front < FTOLERANCE):
         if random() < .5:
            robot.move(0, .2)
         else:
            robot.move(0, -.2)
      else:
         robot.move(.2, 0)

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
