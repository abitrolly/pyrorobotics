# Uses RAVQ to segment input data.
 
from pyro.brain import Brain 
from random import random 
from time import sleep 
import pyro.brain.ravq 
 
class SimpleBrain(Brain): 
   # Only method you have to define is the step method: 
 
   def setup(self): 
      self.blockedFront = 0 
      self.direction = 1 
      self.ravq = pyro.brain.ravq.ARAVQ(10, 1.75, 3.75, .1) 
      self.ravq.setHistory(0)
      self.ravq.openLog('ravq_2.log')
      self.counter = 0 
      self.getRobot().startService('truth') 
      self.getRobot().set('range', 'units', 'ROBOTS') 

   def avoidObstacles(self): 
      robot = self.getRobot() 
 
      """ 
      Determines next action, but doesn't execute it. 
      Returns the translate and rotate values. 
       
      When front is blocked, it picks to turn away from the 
      self.direction with the minimum reading and maintains that 
      turn until front is clear. 
      """ 
      minRange = 0.50
      maxRange = 1.50
      rand = random() * 0.5
      minFront = robot.get('range', 'value', 'front', 'min')[1] 
      minLeft  = robot.get('range', 'value', 'front-left', 'min')[1] 
      minRight = robot.get('range', 'value', 'front-right', 'min')[1] 
      left =  robot.get('range', 'value', 'left', 'min')[1]
      right = robot.get('range', 'value', 'right', 'min')[1]
      
      if minFront < minRange: 
         if not self.blockedFront: 
            if right < left: 
               self.direction = 1 
            else:    
               self.direction = -1 
         self.blockedFront = 1 
         return [0, self.direction * rand] 
       
      elif minLeft < minRange: 
         if self.blockedFront: 
            return [0, self.direction * rand] 
         else: 
            return [rand, -rand] 
      elif minLeft > maxRange:
         if self.blockedFront:
            return [0, self.direction * rand]
         else:
            return [rand, rand]
      elif minRight < minRange: 
         if self.blockedFront: 
            return [0, self.direction * rand] 
         else: 
            return [rand, rand] 
      else: 
         self.blockedFront = 0 
         return [0.5, 0.0]
   
   def recordRAVQ(self): 
      all = self.getRobot().get('range', 'value', 'all') 
      self.ravq.input(all)
      if self.counter % 1000 == 0:
         self.ravq.logHistory(0, str(self.getRobot().dev.get_truth_pose()))
 
   def step(self): 
      print self.counter 
      target = self.avoidObstacles() 
      self.getRobot().move(target[0], target[1]) 
      self.recordRAVQ()          
      if self.counter == 5000:
         self.ravq.logRAVQ()
         self.ravq.closeLog()
         self.ravq.saveRAVQToFile('ravq_2.pck')
         self.pleaseStop()

      self.counter += 1 
 
def INIT(engine): 
   return SimpleBrain('SimpleBrain', engine) 
