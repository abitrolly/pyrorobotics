from pyro.camera import Camera, CBuffer
from pyro.camera.aibo.aibo import Aibo
from math import pi, sin, cos
import threading
import time

PIOVER180 = pi / 180.0

class CameraThread(threading.Thread):
    """
    A camera thread class, because Aibo feeds it to us
    as fast as we can eat em!
    """
        
    def __init__(self, runable):
        """
        Constructor, setting initial variables
        """
        self.runable = runable
        self._stopevent = threading.Event()
        self._sleepperiod = 0.01
        threading.Thread.__init__(self, name="CameraThread")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
           self.runable.cameraDevice.updateMMap(0)
           self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class AiboCamera(Camera):
   """
   """
   def __init__(self, robot, visionSystem = None):
      """
      """
      self.robot = robot
      if self.robot.menuData["TekkotsuMon"]["RawCamServer"][2] == "off":
         print "Turning on 'RawCamServer'..."
         self.robot.menu_control.s.send( "0\n")
      time.sleep(1)
      self.cameraDevice = Aibo( self.robot.host )
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
      self.thread = CameraThread(self)
      self.thread.start()

   def _update(self):
      try:
         # may need to add a lock here, and above
         # to make sure we don't crash into each other
         self.cameraDevice.updateMMap(1)
      except:
         print "error in AiboCamera data format"
      self.processAll() # filters

   def destroy(self):
      self.thread.join()
