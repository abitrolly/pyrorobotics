# A Pyro brain to clean up two rooms
# After Russell and Norvig AIMA

from pyro.brain import Brain

class CleanUp(Brain):
      
   def step(self):
      if self.get("robot/Status") == "Dirty":
         self.robot.move("Suck")
      elif self.get("robot/Location") == "A":
         self.robot.move("Right")
      elif self.get("robot/Location") == "B":
         self.robot.move("Left")

def INIT(engine):
   return CleanUp('AIMA', engine)
      
