# A Pyrobot brain to clean up two rooms using a
# simple reflex brain.After Russell and Norvig
# (AIMA, 2003) page 46.

from pyrobot.brain import Brain

class SimpleBrain(Brain):
   def ReflexVaccumAgent(self, location, status):
      if status == "dirty": return "suck"
      elif location == "A": return "right"
      elif location == "B": return "left"
      
   def step(self):
      # ask the robot for perceptions:
      location = self.get("robot/location")
      status = self.get("robot/status")
      # call the agent program
      action = self.ReflexVaccumAgent(location, status)
      # make the move:
      self.robot.move(action)

# a way of returning the brain instance:
def INIT(engine):
   return SimpleBrain('My Vaccum Robot Brain', engine)
      
