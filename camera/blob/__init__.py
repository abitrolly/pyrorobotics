from pyro.camera import Camera, CBuffer
from pyro.camera.blob.blob import Blob
import time

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot, camera = "camera0", depth = 3, interval = 1.0,
                visionSystem = None):
      """
      """
      self.robot = robot
      self.deviceName = self.robot.startDevice('blob')
      self.blobData = self.robot.getDeviceData(self.blobName)
      if len(self.blobData[0]) == 2: 
         self.width, self.height = self.blobData[0]
      else:
         raise "didn't load blob camera"
      self.depth = depth
      self.interval = interval
      self.lastUpdate = 0
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
      self.data = CBuffer(self.cbuf)
      
   def _update(self):
      currentTime = time.time()
      if currentTime - self.lastUpdate > self.interval:
         blobdata = self.robot.getDeviceData('blob')[1]
         self.cameraDevice.updateMMap(blobdata)
         self.processAll()
         self.lastUpdate = currentTime
