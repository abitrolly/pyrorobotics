# A bare brain

from pyro.brain import Brain
from time import sleep

def process(self):
   self.apply('match', 255 , 166 , 120 , )
   self.apply('match', 132 , 52 , 46 , )
   #self.apply("match", ) 
   #camera.apply("maxBlobs", 0, 1, 255, "mass") 

class SimpleBrain(Brain):

   def setup(self, **args):
      print "Loading arg: '%s'" % args.get('my_arg')
      self.camera = self.getRobot().startService("FakeCamera")[0]
      self.camera.makeWindow()
      self.camera.setVisionCallBack( lambda self=self: process(self.camera) )
      # initialize your vars here!
      
   # Only method you have to define is the step method:

   def step(self):
      print "robot setpping..."
            

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine, my_arg = "testing")
      
