from pyro.camera import *

class FakeCamera(Camera):
   """
   A Fake camera class. Simulates live vision. Call update() to get image.
   file is a parameter that indicates a full or relative file template
   starting with 0. Leave empty to use the system files.
   """
   def __init__(self, file = None, start = 0, incr = 1):
      self.start = start
      self.incr = incr
      self.count = start
      if file == None:
         from os import getenv
         pyrodir = getenv('PYRO')
         if pyrodir == None:
            print "WARNING: environment variable PYRO not defined"
            print "info   : trying /usr/local/pyro..."
            pyrodir = "/usr/local/pyro"
         self.file = pyrodir + "/vision/snaps/som-%d.ppm"
      else:
         self.file = file 
      Camera.__init__(self, 0, 0) # will get info from file

   def _update(self):
      if not file_exists(self.file % self.count):
         self.count = self.start
      if not file_exists(self.file % self.count):
         from sys import exit
         print "Can't find images:", self.file % self.count
         exit(1)
      self.loadFromFile(self.file % self.count)
      self.count += self.incr
