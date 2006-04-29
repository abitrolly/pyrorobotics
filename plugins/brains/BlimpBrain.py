from pyrobot.brain import Brain

class BlimpBrain(Brain):
   def setup(self):
      self.conv = 152.0/332.0
      self.targetDistance = 100.0
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
         
   def step(self):
      freq, value, total = self.robot.frequency[0].getFreq(1)
      distance = freq * self.conv
      diff = self.targetDistance - distance
      amount = max(min(diff / 200.0, 1.0), -1.0)
      print -amount
      self.robot.moveZ(-amount)

def INIT(engine):
   return BlimpBrain("BlimpBrain", engine)
      
