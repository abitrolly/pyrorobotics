from pyro.camera import Camera, CBuffer
from pyro.camera.blob.blob import Blob

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot, depth = 3, interval = 1.0,
                visionSystem = None):
      """
      """
      self.robot = robot
      self.robot.startService('blob')
      self.blobData = self.robot.getServiceData('blob')
      if len(self.blobdata[0]) == 2: 
         self.width, self.height = self.blobdata[0]
      else:
         raise "didn't load blob camera"
      self.depth = depth
      self.colorpos = { (255, 255, 255) : 0,
                        (255, 0, 0): 1,
                        (0, 255, 0) : 2, 
                        (0, 0, 255) : 3,
                        (0, 255, 255) : 4,
                        (255, 255, 0) : 5, 
                        (255, 0, 255) : 6, 
                        (0, 0, 0) : 7}
      self.colorpal = [ (255, 255, 255), 
                        (255, 0, 0),
                        (0, 255, 0),
                        (0, 0, 255),
                        (0, 255, 255),
                        (255, 255, 0),
                        (255, 0, 255),
                        (0, 0, 0) ]      
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
      
   def _update(self):
      currentTime = time.time()
      if currentTime - self.lastUpdate > self.interval:
         self.cameraDevice.updateMMap(None)
         if self.vision != None:
            self.vision.processAll()
         self.lastUpdate = currentTime



