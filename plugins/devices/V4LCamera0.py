from pyro.camera.v4l import V4LCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera" : V4LCamera( 160, 120, channel = 0, 
                                  visionSystem = VisionSystem())}
