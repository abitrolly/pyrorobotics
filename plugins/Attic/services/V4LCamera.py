""" A simple loader for a Video for Linux (V4L) frame grabber """

from pyro.camera.v4l import *

def INIT(robot):
    if robot.get("self", "name") == "Aria":
        # Pioneers. You may have to set channel by hand to one that works
        ch = 0 # channel
    else:
        # For framegrabbers:
        # Channel -  0: television; 1: composite; 2: S-Video
        ch = 1 # channel
    return {"V4LCamera" : V4LGrabber( 160, 120, channel = ch)}
    #384, 240, channel = ch)}
