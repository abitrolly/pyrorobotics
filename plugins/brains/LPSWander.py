# A bare brain with a Local Perceptual View

from pyro.brain import Brain
from random import random
from time import sleep
from pyro.map.lps import LPS

class SimpleBrain(Brain):
   def setup(self):
      # create the Local Perceptiual Space window
      self.lps = LPS( 10, 10)

   def destroy(self):
      self.lps.destroy()

   def step(self):
      robot = self.getRobot()
      self.lps.reset() # reset counts
      self.lps.sensorHits(robot, 'sonar')
      self.lps.redraw()

      FTOLERANCE = 1.0
      LTOLERANCE = 1.0
      RTOLERANCE = 1.0

      left = robot.get('range', 'value', 'left', 'min')[1]
      right = robot.get('range', 'value', 'right', 'min')[1]
      front = robot.get('range', 'value', 'front', 'min')[1]
      return
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
      
