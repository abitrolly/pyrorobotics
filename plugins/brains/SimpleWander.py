# A bare brain

from pyro.brain import Brain

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def step(self):
      TOLERANCE = 1.0

      left = min(self.get('robot/range/left/value'))
      right = min(self.get('robot/range/right/value'))
      front = min(self.get('robot/range/front/value'))

      #print "left", left, "front", front, "right", right

      if (left < TOLERANCE and right < TOLERANCE):
         self.robot.move(0, .2)
      elif (right < TOLERANCE):
         self.robot.move(0, .2)
      elif (left < TOLERANCE):
         self.robot.move(0, -.2)
      elif (front < TOLERANCE): 
         self.robot.move(0, .2) # arbitrarily turn one way
      else:
         self.robot.move(.2, 0)

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
