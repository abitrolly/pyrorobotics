from pyro.camera.v4l import V4LGrabber
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"V4LCamera" : V4LGrabber( 384, 240, channel = 0,
                                      visionSystem = VisionSystem())}
