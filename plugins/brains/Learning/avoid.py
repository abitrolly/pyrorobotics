# robot goes forward and then slows to a stop when it detects something 
  
from pyro.brain import Brain 
  
class NNBrain(Brain): 
          
   # Give the front two sensors, decide the next move 
   def determineMove(self, sensors): 
      if sensors[2] < 0.5 or sensors[3] < 0.5:   # about to hit soon, STOP 
         print "collision imminent, stopped" 
         return(0) 
      elif sensors[2] < 0.8 or sensors[3] < 0.8:  # detecting something, SLOWDOWN 
         print "object detected" 
         return(0.1) 
      else: 
         print "clear"      # all clear, FORWARD 
         return(0.3)

   def determineTurn(self, sensors): 
      # return a value between -1 and 1 based on sensors:
      return 0.0
     
   def step(self): 
      robot = self.getRobot()
      sensors = robot.get('range', 'value', 'all')
      translate = self.determineMove(sensors) 
      rotate = self.determineTurn(sensors) 
      print "front sensors", sensors[2], sensors[3] 
      robot.move(translate, rotate) 
        
def INIT(robot): 
   return NNBrain('NNBrain', robot) 
