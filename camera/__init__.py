# A Base Camera class

from pyro.vision import *
from pyro.brain.fuzzy import *

import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk
import os

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
      self.center()
      self.update() # call it once to initialize
      
   def _update(self):
      """
      This method should be overloaded to interface with the camera.
      """
      pass

   def update(self, detectMotion = 0, threshold = 25):
      """
      Update method for getting next sequence from a video camera.
      Also can detectMotion.
      """
      if detectMotion:
         self.previous = self.data[:]
      self._update()
      if detectMotion:
         self.motion = Bitmap(self.width, self.height)
         self.movedPixelCount = 0
         for x in range(self.width):
            for y in range(self.height):
               if (abs((self.previous[(x + y * self.width) * self.depth + 0] +
                        self.previous[(x + y * self.width) * self.depth + 1] +
                        self.previous[(x + y * self.width) * self.depth + 2])
                       / 3.0 -
                       (self.get(x, y, 0) +
                        self.get(x, y, 1) +
                        self.get(x, y, 2)) / 3.0) > threshold):
                  self.motion.set(x, y, 1)
                  self.movedPixelCount += 1
         print "moved:", self.movedPixelCount



   # pan, tilt, and zoom methods
   # camera implementations will need to over-write these
         
   # -1 to 1, -1 is left, 1 is right
   def pan(self, speed):
      if speed < 0:
         print "pan left at speed", -1*speed
      elif speed > 0:
         print "pan right at speed", speed
      else:
         print "pan zero"
   def panTo(self, panAngle):
      print "pan to", panAngle
   def getPan(self):
      print "unknown pan angle"
      return 0

   # -1 to 1, -1 is down, 1 is up
   def tilt(self, speed):
      if speed < 0:
         print "tilt down at speed", -1*speed
      elif speed > 0:
         print "tilt up at speed", speed
      else:
         print "tilt zero"
   def tiltTo(self, tiltAngle):
      print "tilt to", tiltAngle
   def getTilt(self):
      print "unknown tilt angle"
      return 0

   # -1 to 1, -1 is back, 1 is forward
   def zoom(self, speed):
      if speed < 0:
         print "zoom out at speed", -1*speed
      elif speed > 0:
         print "zoom in at speed", speed
      else:
         print "zoom zero"
   def zoomTo(self, zoomAmount):
      print "zoom to", zoomAmount         
   def getZoom(self):
      print "unknown tilt amount"
      return 0

   def center(self):
      self.panTo(0)
      self.tiltTo(0)
      self.zoomTo(0)

   # pan, tilt, and zoom to frame an image in the camera
   # (does not need to be over-written in camera subclassing)
   # ----------------------------------------
   # *bound_ul* and *bound_lr* should be the upper-left and lower-right
   #    bounds of the desired frame, passed as instances of Point
   # *fill* specifies the percentage of the screen to fill according
   #    to the dominant dimension of the image
   # *max_movement_speed* where movement is pan,tilt,zoom specifies
   #    the maximum speed for each type of movement
   # -----------------------------------
   # returns a sum of squares of the three speeds (before normalization
   # by the maximum speeds).  as the return value approaches zero,
   # the desired framing is close to being achieved (probably a bad idea
   # to wait until it actually is zero...)

   # need to worry about self.width and self.height being zero...?

   def frame(self, bound_ul, bound_lr, fill=0.6, \
             max_pan_speed = 1.0, max_tilt_speed = 1.0, max_zoom_speed = 1.0):
      frameWidth   = bound_lr.x - bound_ul.x
      frameHeight  = bound_lr.y - bound_ul.y
      frameCenter  = Point(float(bound_ul.x)+float(frameWidth)/2.0, \
                           float(bound_ul.y)+float(frameHeight)/2.0)
      cameraCenter = Point(float(self.width)/2.0, float(self.height)/2.0)

      # fuzzily pan and tilt to center image:
      if frameCenter.x > cameraCenter.x:   # pan right
         pan_mult = float(Fuzzy(cameraCenter.x, \
                                cameraCenter.x + float(self.width)/4.0) \
                          >> frameCenter.x)
      else:   # pan left
         pan_mult = -1.0*float(Fuzzy(cameraCenter.x - float(self.width)/4.0, \
                                     cameraCenter.x) << frameCenter.x)
      if frameCenter.y > cameraCenter.y:   # tilt down
         tilt_mult = -1.0*float(Fuzzy(cameraCenter.y, \
                                 cameraCenter.y + float(self.height)/4.0) \
                           >> frameCenter.y)
      else:   # tilt up
         tilt_mult = float(Fuzzy(cameraCenter.y - float(self.height)/4.0, \
                                      cameraCenter.y) << frameCenter.y)

      # fuzzily zoom so that image fills the desired percentage of the screen:
      if frameWidth*self.height > frameHeight*self.width:  # width is dominant
         frameParam = frameWidth
         targetParam = self.width
      else:  # height is dominant
         frameParam = frameHeight
         targetParam = self.height
      if frameParam > fill*float(targetParam):  # zoom out
         zoom_mult = -1.0*float(Fuzzy(fill*float(targetParam), targetParam) \
                                >> frameParam)
      else:  # zoom in
         zoom_mult = float(Fuzzy(0.0, fill*float(targetParam)) << frameParam)

      self.pan(pan_mult*max_pan_speed)
      self.tilt(tilt_mult*max_tilt_speed)
      self.zoom(zoom_mult*max_zoom_speed)

      return(float(pan_mult*pan_mult + tilt_mult*tilt_mult +  \
                   zoom_mult*zoom_mult)/3.0)

   # the methods in PyroImage for color filtering look pretty
   # wacky at the moment...
   
   def track(self, cutoff, cutoff2='unset', mode='brightness', fill=0.4):
      # preset modes
      if mode == 'yellow':
         mode = 'rg/b'
         cutoff2 = cutoff
      
      if cutoff2 == 'unset':
         cutoff2 = cutoff
      bitmap = self.getBitmap(cutoff,cutoff2,mode)
      blobdata = Blobdata(bitmap)
      blobdata.sort(mode="wacky")
      if blobdata.nblobs == 0:
         self.pan(0)
         self.tilt(0)
         self.zoom(0)
      else:
         targetBlob = blobdata.bloblist[0]
         self.frame(targetBlob.ul, targetBlob.lr, fill)

   def getImage(self):
      raise "MethodNotDefined", "getImage()"

   def makeWindow(self):
      self.window = Tkinter.Toplevel()
      while self.window.tk.dooneevent(2): pass
      self.window.wm_title("pyro@%s: Camera View" \
                           % os.getenv('HOSTNAME') )
      self.im = self.getImage()
      self.image = ImageTk.PhotoImage(self.im)
      self.label = Tkinter.Label(self.window, image=self.image, bd=0)
      #self.label = Tkinter.Label(self.window, bd=0)
      #self.label.configure(image=self.image)
      self.label.pack({'fill':'both', 'expand':1, 'side': 'left'})

   def updateWindow(self):
      self.update()
      while self.window.tk.dooneevent(2): pass
      self.im = self.getImage()
      self.image = ImageTk.PhotoImage(self.im)
      self.label.configure(image = self.image)

if __name__ == '__main__':
   from os import getenv
   
   mycam = Camera(0,0)
   mycam.loadFromFile(getenv('PYRO') + "/vision/snaps/som-21.ppm")      
#   mycam.pan(-0.5)
#   print ""
#   camspeed = mycam.frame(Point(35,10),Point(40,37),fill=0.5)
#   print camspeed
#   mycam.grayScale()
#   mycam.getColorFilter(.1, .2, .3)
#   mycam.resetToColor(.5,.5,0.0)
   mycam.track(cutoff=4.0,mode='yellow')
#   mycam.track(mode='red')
