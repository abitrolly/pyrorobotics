
from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *
import time

class ArmToCenter(Behavior):
   def init(self):
      self.Effects('LElbow Rot', .001)
      self.Effects('LShoulder Pron', .001)
      self.Effects('LWrist Rot', .001)
      

   def update(self):
      should_val = self.getRobot().getValByName('LShoulder Pron')
      elbow_val = self.getRobot().getValByName('LElbow Rot')
      wrist_val = self.getRobot().getValByName('LWrist Rot')

      self.IF(Fuzzy(0, .18) << elbow_val, 'LElbow Rot', .02)
      self.IF(Fuzzy(0, .8) << should_val, 'LShoulder Pron', -.02)
      self.IF(Fuzzy(0, .2) << wrist_val, 'LWrist Rot', .02)
              

class MoveState(State):
   def init(self):
      self.add(ArmToCenter(1))

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
               
   
