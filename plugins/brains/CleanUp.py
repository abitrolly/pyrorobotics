# A Pyro brain to clean up two rooms
# After Russell and Norvig AIMA

from pyro.brain import Brain

class CleanUp(Brain):
      
   def step(self):
      if self.get("robot/status") == "dirty":
         self.robot.move("suck")
      elif self.get("robot/location") == "A":
         self.robot.move("right")
      elif self.get("robot/location") == "B":
         self.robot.move("left")

def INIT(engine):
   return CleanUp('AIMA', engine)
      
