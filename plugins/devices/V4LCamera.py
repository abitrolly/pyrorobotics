from pyro.camera.v4l import V4LGrabber
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera" : V4LGrabber( 384, 240, channel = 0,
                                   visionSystem = VisionSystem())}
