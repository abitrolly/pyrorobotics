from pyro.camera.fake import FakeCamera
from pyro.vision.example.myvision import myVision

def INIT(robot):
    return {"FakeCamera": FakeCamera(visionSystem = myVision())}
