from pyro.camera.blob import BlobCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": BlobCamera(robot, visionSystem = VisionSystem())}
