# A (slow) BTTV Camera Interface
# FIX: need to have a version that loads, stays open, and grabs

from pyro.camera import *
from os import getenv, system
from pyro.brain import Brain
from pyro.robot.saphira import *


class BT848Camera(Camera):
   """
   BT848 Camera Shell Interface. Call update() to get image.
   """
   def __init__(self, mover, width=48, height=32): # port='/dev/video0'):
      self.mover = mover
      self.width = width
      self.height = height
      #self.port = port
      self.pyropath = getenv('PYRO')
      self.user = getenv('USER')
      self.panlimit = 90
      self.tiltlimit = 20
      self.zoomlimit = 0  # zoom doesn't really seem to work yet
#      Camera.__init__(self, self.width, self.height) # will get info from file

   def _update(self):
      print "%s/camera/bt848/bt848grab /tmp/pyro-camera-%s.ppm %d %d" % \
	(self.pyropath, self.user, self.width, self.height)
      system("%s/camera/bt848/bt848grab /tmp/pyro-camera-%s.ppm %d %d" % \
	(self.pyropath, self.user, self.width, self.height))
      if not file_exists("/tmp/pyro-camera-%s.ppm" % self.user):
         raise "Can't find image!"
      self.loadFromFile('/tmp/pyro-camera-%s.ppm' % self.user)

   def display(self):
      system("xv /tmp/pyro-camera-%s.ppm &" % self.user)

   def getPan(self):
      return CameraMover_getPanAngle(self.mover)
   def getTilt(self):
      return CameraMover_getTiltAngle(self.mover)
   def getZoom(self):
      return CameraMover_getZoomAmount(self.mover)

   def panTo(self, panAngle):
      tiltAngle = self.getTilt()
      CameraMover_PanTilt(self.mover, panAngle, tiltAngle)
   def tiltTo(self, tiltAngle):
      panAngle = self.getPan()
      CameraMover_PanTilt(self.mover, panAngle, tiltAngle)
   def panTiltTo(self, panAngle, tiltAngle):
      CameraMover_PanTilt(self.mover, panAngle, tiltAngle)      
   def zoomTo(self, zoomAmount):
      CameraMover_Zoom(self.mover, zoomAmount)
   def center(self):
      CameraMover_Center(self.mover)

   def pan(self, speed):
      da = int(10.0*speed)
      if da == 0:
	 if speed < 0:
	    da = -1
	 elif speed > 0:
	    da = 1
      panAngle = self.getPan() + da
      if panAngle > self.panlimit:
  	 panAngle = self.panlimit
      elif panAngle < -self.panlimit:
	 panAngle = -self.panlimit
      self.panTo(panAngle)
   def tilt(self, speed):
      da = int(5.0*speed)
      if da == 0:
	 if speed < 0:
	    da = -1
	 elif speed > 0:
	    da = 1
      tiltAngle = self.getTilt() + da
      if tiltAngle > self.tiltlimit:
  	 tiltAngle = self.tiltlimit
      elif tiltAngle < -self.tiltlimit:
	 tiltAngle = -self.tiltlimit
      self.tiltTo(tiltAngle)
   def zoom(self, speed):
      da = int(1.0*speed)
      if da == 0:
	 if speed < 0:
	    da = -1
	 elif speed > 0:
	    da = 1
      zoomAngle = self.getZoom() + da
      if zoomAngle > self.zoomlimit:
  	 zoomAngle = self.zoomlimit
      elif zoomAngle < -self.zoomlimit:
	 zoomAngle = -self.zoomlimit
      self.zoomTo(zoomAngle)

if __name__ == '__main__':
   print file_exists("/tmp/pyro-camera-%s.ppm" % 'robot')
   cam = BT848Camera()
