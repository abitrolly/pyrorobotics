from pyro.camera.v4l import V4LCamera
from pyro.vision.cvision import VisionSystem
from pyro.system.share import ask

def INIT(robot):
    retval = ask("Please enter the parameters for the Video4Linux Camera",
                 (("Width", "160"),
                  ("Height", "120"),
                  ("Channel", "0"),                  
                  ))
    if retval["ok"]:
        return {"camera" : V4LCamera( int(retval["Width"]), 
                                      int(retval["Height"]), 
                                      channel = int(retval["Channel"]), 
                                      visionSystem = VisionSystem())}
    else:
        raise "Cancelled!"
