from pyro.camera import Camera, CBuffer
from pyro.camera.aibo.aibo import Aibo
from math import pi, sin, cos
import time

PIOVER180 = pi / 180.0

class AiboCamera(Camera):
   """
   """
   def __init__(self, robot, visionSystem = None):
      """
      """
      self.robot = robot
      self.cameraDevice = Aibo( robot.host )
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self.cameraDevice)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self.cbuf = self.vision.getMMap()
      self.data = CBuffer(self.cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Aibo Camera View")
      self.devData["subtype"] = "aibo"
      self.data = CBuffer(self.cbuf)

   def _update(self):
      try:
         self.cameraDevice.updateMMap()
      except TypeError:
         print "error in AiboCamera data format"
      self.processAll() # filters
