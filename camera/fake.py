from pyro.camera import *

class FakeCamera(Camera):
   """
   A Fake camera class. Simulates live vision. Call update() to get image.
   """
   def __init__(self):
      self.count = 0
      Camera.__init__(self, 0, 0) # will get info from file

   def _update(self):
      from os import getenv
      pyrodir = getenv('PYRO')
      if not file_exists(pyrodir + "/vision/snaps/som-%d.ppm" % self.count):
         self.count = 0
      if not file_exists(pyrodir + "/vision/snaps/som-%d.ppm" % self.count):
         from sys import exit
         print "Can't find $PYRO/vision/snaps/ images!"
         sys.exit(1)
      self.loadFromFile(pyrodir + "/vision/snaps/som-%d.ppm" % self.count)
      self.count += 1
