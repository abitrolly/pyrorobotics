from pyro.camera.fake import FakeCamera
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    return {"FakeCamera": FakeCamera(pattern = "vision/sample/vision-?.ppm", start = 0, limit = 1, interval = 2, visionSystem = VisionSystem())}
