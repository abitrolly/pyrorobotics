from pyro.camera.v4l import *

def INIT():
    return V4LGrabber(384, 240)
