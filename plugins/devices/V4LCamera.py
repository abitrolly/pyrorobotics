from pyro.camera.v4l import V4LCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera" : V4LCamera( 384, 240, channel = 0,
                                  visionSystem = VisionSystem())}
