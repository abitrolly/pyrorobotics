from pyro.camera.fake import FakeCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": FakeCamera(visionSystem = VisionSystem())}
