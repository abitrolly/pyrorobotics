from v4l import V4L      # cameraDevice
from pyro.camera import Camera, CBuffer

class V4LCamera(Camera):
   """
   A Wrapper class for the C fuctions that capture data from the Camera.
   It uses the Video4linux API, and the image is kept in memory through
   an mmap.
   """
   def __init__(self, width, height, depth = 3,
                device = '/dev/video0', channel = 1, title = None,
                visionSystem = None, visible = 1):
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
         self.cameraDevice.setRGB( 2, 1, 0)
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
      self.rgb = (2, 1, 0) # offsets to BGR
      self.format = "BGR"
      Camera.__init__(self, width, height, depth, title = title,
                      visible = visible)
      self.devData["subtype"] = "video4linux"
      self.devData["source"] = device
      self.data = CBuffer(self.cbuf)

   def _update(self):
      """
      Since data is mmaped to the capture card, all we have to do is call
      refresh.
      """
      try:
         self.cameraDevice.updateMMap()
         self.processAll()
      except:
         print "v4l: updateMMap() failed"

