# A bare brain

from pyro.brain import Brain
from time import sleep

class SimpleBrain(Brain):

   def setup(self, **args):
      print "Loading arg: '%s'" % args.get('my_arg')
      self.camera = self.getRobot().startService("FakeCamera")[0]
      # initialize your vars here!
      
   # Only method you have to define is the step method:

   def step(self):
      self.camera.sleepTime=2.0  #sleep for 2 seconds after filters 
      self.camera.sleepFlag = 1  #turn sleep flag on 
      self.camera.lockCamera = 1 #lock the buffer 
      self.camera.superColor("red",0) 
      self.camera.maxBlobs(0, 1, 255, "mass") 
      self.camera.lockCamera = 0 #unlock the buffer 

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine, my_arg = "testing")
      
