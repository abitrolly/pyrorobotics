from pyro.camera.robocup import RobocupCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": RobocupCamera(robot, visionSystem = VisionSystem())}
