# A bare brain 
 
from pyro.brain import Brain 
from random import random 
from time import sleep 
import pyro.brain.ravq 
 
class SimpleBrain(Brain): 
   # Only method you have to define is the step method: 
 
   def setup(self): 
      self.blockedFront = 0 
      self.direction = 1 
      self.ravq = pyro.brain.ravq.ARAVQ(20, .7, 4, .1) 
      self.ravq.setHistory(0) 
      self.counter = 0 
      self.getRobot().startService('truth') 
             
   def avoidObstacles(self): 
      robot = self.getRobot() 
 
      """ 
      Determines next action, but doesn't execute it. 
      Returns the translate and rotate values. 
       
      When front is blocked, it picks to turn away from the 
      self.direction with the minimum reading and maintains that 
      turn until front is clear. 
      """ 
      minRange = 1.0 
      rand = random() 
      minFront = robot.get('range', 'value', 'front', 'min')[1] 
      minLeft  = robot.get('range', 'value', 'front-left', 'min')[1] 
      minRight = robot.get('range', 'value', 'front-right', 'min')[1] 
       
      if minFront < minRange: 
         if not self.blockedFront: 
            if minRight < minLeft: 
               self.direction = 1 
            else:    
               self.direction = -1 
         self.blockedFront = 1 
         return [0, self.direction * rand] 
       
      elif minLeft < minRange: 
         if self.blockedFront: 
            return [0, self.direction*rand] 
         else: 
            #return [0, -turn] 
            return [rand, -rand] 
             
      elif minRight < minRange: 
         if self.blockedFront: 
            return [0, self.direction*rand] 
         else: 
            #return [0, turn] 
            return [rand, rand] 
      else: 
         self.blockedFront = 0 
         return [0.3, rand] 
 
   def recordRAVQ(self): 
      all = self.getRobot().get('range', 'value', 'all') 
      self.ravq.input(all) 
 
   def step(self): 
      print self.counter 
      target = self.avoidObstacles() 
      self.getRobot().move(target[0], target[1]) 
      self.recordRAVQ()          
      if self.counter % 20 == 0: 
         self.ravq.addLabel(str(self.getRobot().dev.get_truth_pose()), \
                            self.ravq.movingAverage[:]) 
         filename = "ravq_" + str(self.counter) + ".pck" 
         self.ravq.saveRAVQToFile(filename) 
         filename = "ravq_" + str(self.counter) + ".dat" 
         fp = open(filename, 'w') 
         fp.write(str(self.ravq)) 
         fp.close() 
      if self.counter == 2000: 
         self.pleaseStop() 
      self.counter += 1 
 
def INIT(engine): 
   return SimpleBrain('SimpleBrain', engine) 
