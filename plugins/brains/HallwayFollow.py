# robot goes forward and then slows to a stop when it detects something  
   
from pyro.brain import Brain, select
from pyro.brain.conx import *  
from time import *  
   
class Avoid(Brain):

   def setup(self):
      self.inputFile = open('/home/meeden/experiments/srnGov/hallway.dat','w')
      self.targetFile = open('/home/meeden/experiments/srnGov/hallway.out','w')
      self.robot.startDevice("truth")
      self.robot.truth.setPose((1,9,-90))
      self.turnRight = 1

   def destroy(self):
      self.robot.removeDevice("truth")
           
   def determineMove(self, dict):
      front = dict["value"]
      pos = dict["pos"]
      if front < 1.0:   # about to hit soon, STOP
         x,y,h = self.robot.truth.getPose()
         if y > 2 and y < 8: # in middle
            if pos < 4: # sonar on left
               return (0.0, -0.1) # turn right
            else:
               return (0.0, 0.1) # turn left
         else:
            if self.turnRight:
               return(0.0, -0.3)
            else:
               return(0.0, 0.3)
      else:
         x,y,h = self.robot.truth.getPose()
         if y < 2:
            self.turnRight = 0
         elif y > 8:
            self.turnRight = 1
         return(0.3, 0)  
      
   def step(self):  
      front = self.get('/robot/range/front-all/value,pos')
      for val in map(lambda dict: dict["value"], front):
         self.inputFile.write(str(val) + " ")
      self.inputFile.write('\n')
      translation, rotate = self.determineMove(select(min, "value", front))
      self.targetFile.write("%f %f\n" % (translation, (rotate+1)/2.0))
      self.robot.move(translation, rotate)  

def INIT(engine):  
   assert (engine.robot.requires("range-sensor") and
           engine.robot.requires("continuous-movement"))
   return Avoid('Avoid', engine)  

