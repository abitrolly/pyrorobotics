from pyro.camera.fake import FakeCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"FakeCamera": FakeCamera(pattern = "vision/tutorial/test-?.ppm", start = 0, limit = 11, interval = 2, visionSystem = VisionSystem())}
