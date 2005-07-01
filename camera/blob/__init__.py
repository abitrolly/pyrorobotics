from pyrobot.camera import Camera, CBuffer
from pyrobot.camera.blob.blob import Blob
import time

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot, camera = None, depth = 3, visionSystem = None):
      """
      """
      self.robot = robot
      # if no camera given, we'll try a blobfinder
      if camera == None:
         # is there a default one?
         try:
            self.blobfinder = self.robot.blobfinder[0]
         except AttributeError:
            # no,then we'll try to start one:
            self.blobfinder = self.robot.startDevice('blobfinder')
      else:
         # else, you better have supplied a name, like "blobfinder0"
         self.blobfinder = camera
      self.blobHandle = self.blobfinder.handle
      while self.blobHandle.width == 0: pass
      self.width, self.height = self.blobHandle.width,self.blobHandle.height
      self.depth = depth
      self.cameraDevice = Blob(self.width, self.height,
                               self.depth)
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self.cameraDevice)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self._cbuf = self.vision.getMMap()
      # -------------------------------------------------
      self.data = CBuffer(self._cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      print self.width, self.height
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Blob Camera View")
      self.requires = ["blobfinder"]
      self.subtype = "blob"
      self.source = "%s[%d]" % (self.blobfinder.type, self.blobfinder.number)
      self.data = CBuffer(self._cbuf)
      
   def update(self):
      blobs = []
      for i in range(self.blobHandle.blob_count):
         blobs.append( (self.blobHandle.blobs[i].left,
                        self.blobHandle.blobs[i].top,
                        self.blobHandle.blobs[i].right,
                        self.blobHandle.blobs[i].bottom,
                        self.blobHandle.blobs[i].color
                        )
                       )
      self.cameraDevice.updateMMap(blobs)
      self.processAll()
