from pyro.system import share
import grabImage
share.grabImage = grabImage
from pyro.camera import Camera, CBuffer
import time
import PIL

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot, width, height, depth = 3, interval = 1.0):
      """
      """
      robot.startService('blob')
      self.robot = robot
      self.width = width
      self.height = height
      self.createVisionRep = createVisionRep
      self.blobdata = []
      self.blobimage = None
      self.depth = 3
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
      self.cbuf = share.grabImage.grab_image(width, height)
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Blob Camera View")
      self.data = CBuffer(self.cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      
   def _update(self):
      if self.lockCamera == 0 and self.limit > 0:
         currentTime = time.time()
         share.grabImage.refresh_image()
         self.lastUpdate = currentTime

   def __del__(self):
      share.grabImage.free_image()



