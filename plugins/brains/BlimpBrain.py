from pyrobot.brain import Brain

class BlimpBrain(Brain):
   def setup(self):
      self.targetDistance = 1.0 # meters
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      print "sleep between:", self.robot.frequency[0].asyncSleep
      print "sampleTime:", self.robot.frequency[0].sampleTime
         
   def step(self):
      freq, value, total = self.robot.frequency[0].results
      distance = freq * 0.0051 - 0.0472
      diff = self.targetDistance - distance
      amount = max(min(diff / 200.0, 1.0), -1.0)
      print freq, distance
      #self.robot.moveZ(amount)

def INIT(engine):
   return BlimpBrain("BlimpBrain", engine)
      
