from v4l import *
from pyro.camera import *
from UserString import UserString
import types, sys, os

import time
import re

class V4LGrabber(Camera):
   """
   A Wrapper class for the C fuctions that capture data from the Camera.
   It uses the Video4linux API, and the image is kept in memory through
   an mmap.
   """
   def __init__(self, width, height, depth = 3,
                device = '/dev/video0', channel = 1, title = None,
                visionSystem = None):
      """
      Device should be the name of the capture device in the /dev directory.
      This is highly machine- and configuration-dependent, so make sure you
      know what works on your system
      Channel -  0: television; 1: composite; 2: S-Video
      """
      if width < 48:
         raise ValueError, "width must be greater than 48"
      if height < 48:
         raise ValueError, "height must be greater than 48"
      self.device = device
      self.handle=None
      self.cbuf=None
      try:
         self.cameraDevice = V4L(device, width, height, depth, channel)
      except:
         print "v4l: grab_image failed!"
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self.cameraDevice)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self.cbuf = self.vision.getMMap()
      # -------------------------------------------------
      if title == None:
	 title = self.device
      Camera.__init__(self, width, height, depth, title = title)
      self.rgb = (2, 1, 0) # offsets to BGR
      self.format = "BGR"
      self.data = CBuffer(self.cbuf)

   def _update(self):
      """
      Since data is mmaped to the capture card, all we have to do is call
      refresh.
      """
      try:
         self.cameraDevice.updateMMap()
      except:
         print "v4l: refresh_image failed"
      try:
         self.vision.processAll()
      except:
         print "error in vision system?"

if __name__ == "__main__":
   cam = V4LGrabber(384, 240)

   if 1:
      cam.makeWindow()
      while 1:
         cam.updateWindow()

   if 0:
      print "Testing frames per/second:",
      start = time.time()
      for i in range(100):
         print ".",
         sys.stdout.flush()
         cam.update()
      stop = time.time()
      print "done!"
      print "FPS = ", 100.00/ (stop - start)

   if 0:
      print "Saving images:"
      print "test1.tga..."
      cam.saveAsTGA("./test1.tga")
      time.sleep(3)
      print "test1.tga..."
      cam.saveAsTGA("./test2.tga")
      cam.update()
      print "test1.tga..."
      cam.saveAsTGA("./test3.tga")

      print """
      If everything worked, then test1.tga and test2.tga should be identical,
      but test3.tga should have been snapped about a second later.  They are
      all saved in the current directory.
      """
   if 0:
      print "Testing greyscale..."
      cam = V4LGrabber(384, 240, 1)
      cam.save("./testgrey.tga")
      print "Saved testgrey.tga"

   del cam

