from pyro.camera.fake import FakeCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"FakeCamera": FakeCamera(visionSystem = VisionSystem())}
