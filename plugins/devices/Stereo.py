""" A simple loader for a Video for Linux (V4L) frame grabber """

from pyro.camera.v4l import V4LGrabber
from pyro.vision.cvision import VisionSystem

def INIT(robot):
    if robot.get("self", "name") == "Aria":
        # Pioneers. You may have to set channel by hand to one that works
        ch = 0 # channel
    else:
        # For framegrabbers:
        # Channel -  0: television; 1: composite; 2: S-Video
        ch = 1 # channel
    return {"video0" : V4LGrabber( 160, 120, device = "/dev/video0",
                                  channel = ch,
                                  visionSystem = VisionSystem()),
	    "video1" : V4LGrabber( 160, 120, device = "/dev/video1",
                                  channel = ch,
                                  visionSystem = VisionSystem())}

