from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *

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
              

class ArmToBack(Behavior):
   def init(self):
      self.Effects('LElbow Rot', .001)
      self.Effects('LShoulder Pron', .001)
      self.Effects('LWrist Rot', .001)
      
   def update(self):
      should_val = self.getRobot().getValByName('LShoulder Pron')
      elbow_val = self.getRobot().getValByName('LElbow Rot')
      wrist_val = self.getRobot().getValByName('LWrist Rot')

      self.IF(Fuzzy(0, .18) >> elbow_val, 'LElbow Rot', -.02)
      self.IF(Fuzzy(0, .8) >> should_val, 'LShoulder Pron', .02)
      self.IF(Fuzzy(0, .2) >> wrist_val, 'LWrist Rot', -.02)
              

class MoveCenter(State):
   def init(self):
      self.add(ArmToCenter(1))

   def update(self):
      if self.getRobot().getValByName('LElbow Rot') > .16:
         self.goto("MoveBack")

class MoveBack(State):
   def init(self):
      self.add(ArmToBack(1))

   def update(self):
      if self.getRobot().getValByName('LElbow Rot') < 0.1:
         self.goto("MoveCenter")

def INIT(engine):
   brain = BehaviorBasedBrain(engine.robot.controls, engine)
   brain.add(MoveBack())
   brain.add(MoveCenter(1))
   brain.init()
   return brain
