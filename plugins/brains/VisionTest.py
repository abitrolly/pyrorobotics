from pyro.brain import Brain

def process(camera):
   camera.apply('match', 158 , 71 , 48 , )
   camera.apply('match', 225 , 129 , 89 , )
   camera.apply('match', 188 , 109 , 68 , )
   camera.userData = camera.apply("blobify", 0)

class VisionBrain(Brain):
   def setup(self):
      self.camera = self.getRobot().startService("FakeCamera")[0]
      self.camera.makeWindow()
      self.camera.userData = []
      self.camera.addFilter( process )
      
   def step(self):
      # do something with the camera processed data:
      print self.camera.userData
            
def INIT(engine):
   return VisionBrain('SimpleBrain', engine)

