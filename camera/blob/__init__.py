from pyro.camera import Camera, CBuffer
from pyro.camera.blob.blob import Blob
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
            self.deviceName = self.robot.get("/devices/blobfinder0/name")
         except AttributeError:
            # no,then we'll try to start one:
            self.deviceName = self.robot.startDevice('blobfinder')
      else:
         # else, you better have supplied a name, like "blobfinder0"
         self.deviceName = camera
      self.blobData = self.robot.getDeviceData(self.deviceName)
      if len(self.blobData[0]) == 2: 
         self.width, self.height = self.blobData[0]
      else:
         raise "didn't load blob camera"
      self.depth = depth
      self.cameraDevice = Blob(self.width, self.height,
                               self.depth)
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self.cameraDevice)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self.cbuf = self.vision.getMMap()
      # -------------------------------------------------
      self.data = CBuffer(self.cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Blob Camera View")
      self.devData["requires"] = ["blobfinder"]
      self.devData["subtype"] = "blob"
      self.devData["source"] = self.deviceName
      self.data = CBuffer(self.cbuf)
      
   def _update(self):
      blobdata = self.robot.getDeviceData(self.deviceName)[1]
      self.cameraDevice.updateMMap(blobdata)
      self.processAll()
