from pyro.camera.aibo import AiboCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": AiboCamera(robot, visionSystem = VisionSystem())}
