#A basic Behavior showing how ArmorRobot should be used
from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *
import time

class MoveArm(Behavior):
   def init(self):
      self.Effects('LElbow Rot', .1)
      self.Effects('RWrist Rot', .1)

   def update(self):
      self.IF(1, 'LElbow Rot', .05)
      self.IF(1, 'RWrist Rot', .05)

class MoveState(State):
   def init(self):
      self.add(MoveArm(1))

def INIT(robot):
   #It seems that every single class that accesses the controls
   #keeps a copy of the controls dictionary.  Ideally, there would
   #only be one, kept in the actualy Driver, and all the other classes
   #would access it.
   brain = BehaviorBasedBrain(robot.controls, robot)
   
   brain.add(MoveState())
   
   brain.activate('MoveState')
   brain.init()
   return brain
               
   
