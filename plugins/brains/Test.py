# A bare brain

from pyro.brain import Brain
from pyro.robot.playerpuck import *

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def setup(self):
      # create any vars you need here
      self.puck = PlayerPuck("puck1", 8000)

   def step(self):
      #self.robot.move(0, -.2) # negative is to the right!
      print "IR : ----------------------------"
      print "Min distance:", self.robot.getMin().distance
      print "Max distance:", self.robot.getMax().distance

      print "Min angle:", self.robot.getMin().angle
      print "Max angle:", self.robot.getMax().angle

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain("SimpleBrain", engine)
      
