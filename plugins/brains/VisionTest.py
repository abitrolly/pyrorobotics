from pyro.brain import Brain

def process(camera):
   camera.apply('match', 158 , 71 , 48 , )
   camera.apply('match', 225 , 129 , 89 , )
   camera.apply('match', 188 , 109 , 68 , )
   camera.apply("superColor", 1, -1, -1, 0) # rgb weights, 0 = red channel
   camera.apply("threshold", 0, 50) # red channel, 50 > 0
   return camera.apply("blobify", 0) # red channel
   # filters can return values; stored in camera.filterReturnValue

class VisionBrain(Brain):
   def setup(self):
      if "FakeCamera" not in self.robot.getServices():
         self.camera = self.getRobot().startService("TutorialCamera")[0]
      else:
         self.camera = self.getRobot().getService("FakeCamera")
      self.camera.makeWindow()
      self.camera.addFilter( process )
      
   def step(self):
      # do something with the camera processed data:
      print self.camera.filterReturnValue[0]
            
def INIT(engine):
   return VisionBrain('SimpleBrain', engine)

