# A bare brain

from pyro.brain import Brain

class SimpleBrain(Brain):
   # Only method you must define is the step method:

   def setup(self):
      # create any vars you need here
      pass

   def destroy(self):
      # if you need to del or destroy items, do it here
      pass

   def step(self):
      #self.robot.move(0, -.2) # negative is to the right!
      print "IR : ----------------------------"
      print "Min distance:", min(self.get('/robot/range/all/value'))
      print "Max distance:", max(self.get('/robot/range/all/value'))

# -------------------------------------------------------
# This is the interface for calling from the gui.
# Takes one param (the engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain("SimpleBrain", engine)
      
