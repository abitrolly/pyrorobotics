from pyro.camera.fake import *

def INIT(engine):
    # don't need engine.robot in this one
    return FakeCamera()
