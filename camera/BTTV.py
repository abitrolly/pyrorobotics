# A (slow) BTTV Camera Interface
# FIX: need to have a version that loads, stays open, and grabs

from pyro.camera import *
from os import getenv, system

class BTTVCamera(Camera):
   """
   BTTV Camera Shell Interface. Call update() to get image.
   """
   def __init__(self, width = 32, height = 48, port = '/dev/video0'):
      self.width = width
      self.height = height
      self.port = port
      self.user = getenv('USER')
      Camera.__init__(self, width, height) # will get info from file

   def _update(self):
      system("bttvgrab -G %s -f /tmp/pyro-camera-%s.ppm -o ppm -N NTSC -Q -l 1 -S 1 -d q -W %d -w %d" % (self.port, self.user, self.width, self.height))
      if not file_exists('/tmp/pyro-camera-%s.ppm' % self.user):
         raise "Can't find image!"
      self.loadFromFile('/tmp/pyro-camera-%s.ppm' % self.user)
