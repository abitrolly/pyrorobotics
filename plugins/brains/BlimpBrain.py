from pyrobot.brain import Brain

class BlimpBrain(Brain):
   def setup(self):
      self.targetDistance = 1.0 # meters
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
         
   def step(self):
      freq, value, total = self.robot.frequency[0].getFreq(1)
      distance = freq * 0.0051 - 0.0472
      diff = self.targetDistance - distance
      amount = max(min(diff / 200.0, 1.0), -1.0)
      print freq, distance
      #self.robot.moveZ(-amount)
      # 

def INIT(engine):
   return BlimpBrain("BlimpBrain", engine)
      
