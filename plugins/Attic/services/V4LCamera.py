from pyro.camera.v4l import *

def INIT(robot):
    return {"V4LCamera" : V4LGrabber(384, 240)}
