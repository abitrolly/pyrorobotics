from pyro.camera.fake import FakeCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"FakeCamera": FakeCamera(pattern = "vision/tutorial/test-?.ppm", limit = 10, interval = 3, visionSystem = VisionSystem())}
