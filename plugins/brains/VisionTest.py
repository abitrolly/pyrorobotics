from pyro.brain import Brain

def process(camera):
   camera.apply('match', 158 , 71 , 48 , )
   camera.apply('match', 225 , 129 , 89 , )
   camera.apply('match', 188 , 109 , 68 , )
   camera.apply("superColor")
   retval = camera.apply("blobify", 0)
   camera.userData = retval

class VisionBrain(Brain):

   def setup(self):
      self.camera = self.getRobot().startService("FakeCamera")[0]
      self.camera.makeWindow()
      # callback is a function that takes one arg, the camera
      self.camera.setCallback( process )
      
   def step(self):
      print self.camera.userData
            
def INIT(engine):
   return VisionBrain('SimpleBrain', engine)
