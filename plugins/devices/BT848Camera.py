from pyro.camera.bt848 import BT848Camera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera" : BT848Camera( 160, 120, 
                                   visionSystem = VisionSystem())}
