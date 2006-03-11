from pyrobot.camera import Camera, CBuffer # base class
from pyrobot.vision.cvision import VisionSystem

class FourwayCamera(Camera):
   """
   """
   def __init__(self, camera, quad):
      self._camera = camera
      self._quad   = quad
      self._dev = Fourway("", self._camera._cbuf, self._camera.width,
                          self._camera.height, self._camera.depth, quad)
      self.vision = VisionSystem()
      self.vision.registerCameraDevice(self._dev)
      self._cbuf = self.vision.getMMap()
      # -------------------------------------------------
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Fourway Camera View")
      self.data = CBuffer(self._cbuf)

   def update(self):
      self._dev.updateMMap()
      self.processAll()

if __name__ == "__main__":
   camera = FourwayCamera()
   camera.update()
