from pyrobot.brain import Brain
import time

class BlimpBrain(Brain):
   def setup(self):
      self.targetDistance = 1.0 # meters
      self.fp = open("stats", "w")
      self.igain = 0.0
      self.pgain = 0.0
      self.dgain = 0.0
      self.integral = 0.0
      self.old_diff = 0.0
      self.deriv = 0.0
      self.pulseTime = 0.5
      self.dutyCycle = .3
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      self.robot.frequency[0].setSampleTime(0.4)
      print "sleep between:", self.robot.frequency[0].asyncSleep
      print "sampleTime:", self.robot.frequency[0].sampleTime
         
   def step(self):
      freq, value, total, best, bestValue = self.robot.frequency[0].results
      distance = freq * 0.0051 - 0.0472
      #proportional
      diff = self.targetDistance - distance
      #print diff
      self.fp.write("%f\n" % diff)
      self.fp.flush()
      #integral
      self.integral += diff
      #derivative
      self.deriv = diff - self.old_diff
      #correction amount
      amount = (self.integral * self.igain + diff + (self.deriv*self.dgain)) * self.pgain

      if(amount > 0):
         amount +=.19
      else:
         amount -=.19
      amount = max(min(amount, 1.0), -1.0)
      print distance, amount, diff, self.pgain, self.igain, self.dgain
      self.robot.moveZ(amount)
      #time.sleep(self.dutyCycle * self.pulseTime)
      #self.robot.moveZ(0.0)
      #time.sleep(self.pulseTime * (1-self.dutyCycle))
      self.old_diff = diff


def INIT(engine):
   return BlimpBrain("BlimpBrain", engine)
      
