# A bare brain with a Local Perceptual View

from pyro.brain import Brain
from random import random
from time import sleep
from pyro.map.lps import LPS
from pyro.map.gps import GPS

class SimpleBrain(Brain):
   def setup(self):
      # create the Local Perceptiual Space window
      units = self.getRobot().get('range', 'units')
      self.getRobot().set('range', 'units', 'MM')
      sizeMM = self.getRobot().get('range', 'maxvalue') * 3 + \
               self.getRobot().get('self', 'radius')
      self.getRobot().set('range', 'units', units)
      self.lps = LPS( 20, 20,
                      widthMM = sizeMM,
                      heightMM = sizeMM)
      self.gps = GPS(100, 100, widthMM = sizeMM * 5, heightMM = sizeMM * 5)

   def destroy(self):
      self.lps.destroy()
      self.gps.destroy()

   def step(self):
      robot = self.getRobot()
      self.lps.reset() # reset counts
      self.lps.sensorHits(robot, 'range')
      self.lps.redraw()
      self.gps.updateFromLPS(self.lps, robot)
      
      FTOLERANCE = 1.0
      LTOLERANCE = 1.0
      RTOLERANCE = 1.0

      left = robot.get('range', 'value', 'left', 'min')[1]
      right = robot.get('range', 'value', 'right', 'min')[1]
      front = robot.get('range', 'value', 'front', 'min')[1]

      #print "left", left, "front", front, "right", right

      if (left < LTOLERANCE and right < RTOLERANCE):
         robot.move(0, .2)
         sleep(.5)
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
      
