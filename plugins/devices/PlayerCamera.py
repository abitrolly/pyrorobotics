from pyro.camera.player import PlayerCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": PlayerCamera("localhost", 6665, visionSystem = VisionSystem())}
