from pyro.camera.v4l import *

def INIT(engine):
    # don't need engine.robot in this one
    return V4LGrabber(384, 240)
