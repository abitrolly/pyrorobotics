# A (slow) BTTV Camera Interface
# FIX: need to have a version that loads, stays open, and grabs

from pyro.camera import *
from os import getenv, system

class BT848Camera(Camera):
   """
   BT848 Camera Shell Interface. Call update() to get image.
   """
   def __init__(self): #, width = 32, height = 48, port = '/dev/video0'):
      self.width = 0 #width
      self.height = 0 #height
      #self.port = port
      self.pyropath = getenv('PYRO')
      self.user = getenv('USER')
      Camera.__init__(self, self.width, self.height) # will get info from file

   def _update(self):
      print "%s/camera/bt848/bt848grab /tmp/pyro-camera-%s.ppm" % \
	(self.pyropath, self.user)
      system("%s/camera/bt848/bt848grab /tmp/pyro-camera-%s.ppm" % \
	(self.pyropath, self.user))
      if not file_exists("/tmp/pyro-camera-%s.ppm" % self.user):
         raise "Can't find image!"
      self.loadFromFile('/tmp/pyro-camera-%s.ppm' % self.user)

if __name__ == '__main__':
   print file_exists("/tmp/pyro-camera-%s.ppm" % 'robot')
   cam = BT848Camera()