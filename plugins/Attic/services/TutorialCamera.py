from pyro.camera.fake import FakeCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"FakeCamera": FakeCamera(pattern = "/usr/local/pyro/vision/tutorial/test-?.ppm", limit = 10, interval = 3, visionSystem = VisionSystem())}
