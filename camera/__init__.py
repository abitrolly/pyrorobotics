# A Base Camera class

from pyro.vision import *

class Camera(PyroImage):
   """
   A base class for Camera
   """
   def __init__(self, width, height, depth = 3):
      """
      To specify the resolution of a particular camera, overload this
      constructor with one that initalizes the dimensions itself
      """
      PyroImage.__init__(self, width, height, depth, 0)
      self.update() # call it once to initialize 
      
   def _update(self):
      """
      This method should be overloaded to interface with the camera.
      """
      raise "The Camera._update  method should be overloaded!"

   def update(self, detectMotion = 0):
      """
      Update method for getting next sequence from a video camera.
      Also can detectMotion.
      """
      if detectMotion:
         self.previous = self.data[:]
      self._update()
      if detectMotion:
         self.motion = Bitmap(self.width, self.height)
         movedPixelCount = 0
         for x in range(self.width):
            for y in range(self.height):
               if (abs((self.previous[(x + y * self.width) * self.depth + 0] +
                        self.previous[(x + y * self.width) * self.depth + 1] +
                        self.previous[(x + y * self.width) * self.depth + 2])
                       / 3.0 -
                       (self.get(x, y, 0) +
                        self.get(x, y, 1) +
                        self.get(x, y, 2)) / 3.0) > .1):
                  self.motion.set(x, y, 1)
                  movedPixelCount += 1
         print "moved:", movedPixelCount

