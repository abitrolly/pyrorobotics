from pyro.camera import *
from grabImage import *
from UserString import UserString
import types
import sys

import PIL.PpmImagePlugin
from Tkinter import *
import Image, ImageTk
import time

class V4LGrabber(Camera):
   """
   A Wrapper class for the C fuctions that capture data from the Khepera robot.
   It uses the Video4linux API, and the image is kept in memory through
   an mmap.

   Thought -- I have no idea what will happen if two instances of this
   class are created.  It might be harmless, or it might cause a crash.
   I think if you call update on one of them, both will be updated.  Maybe
   it wasn't such a good idea to pass the mmap directly back to Python.

   It looks like trying to instanciate a V4LGrabber, deleting it, and trying
   to instanciate another causes problems with device busy on the video device.
   I'm not sure why.
   """
   def __init__(self, width, height, depth = 3, device = '/dev/video0'):
      """
      Currently, if depth is any number other than 1 or 3, an exception
      will be raised.  I plan on implementing various color depths soon.

      Device should be the name of the capture device in the /dev directory.
      This is highly machine- and configuration-dependent, so make sure you
      know what works on your system
      """
      if depth == 1:
         self.color = 0
      elif depth == 3:
         self.color = 1
      else:
         raise "Color depth settings other than one or three not yet supported"

      if width < 48:
         raise ValueError, "Width must be greater than 48."
      if height < 48:
         raise ValueError, "Height must be greater than 48."

      self.width = width
      self.height = height
      
      self.device = device
      #handle is the file handle for device
      #it needs to get passed back to refresh
      #and free
      self.handle=None
      self.cbuf=None
      self.size, self.depth, self.handle, self.cbuf = \
                 grab_image(device, width, height, self.color)
      self.depth /= 8
      self.data = CBuffer(self.cbuf)

   def _update(self):
      """
      Since data is mmaped to the capture card, all we have to do is call
      refresh.
      """
      refresh_image(self.handle, self.width, self.height, self.depth*8)

   def __del__(self):
      """
      DO NOT REMOVE THIS!
      This deconstructor method makes sure that the mmap is freed before the
      Camera is deleted.
      """
      if dir(self).count('handle') == 1 and self.handle and self.cbuf:
         #if __init__ was not successful in acquiring the video device,
         #a call to free_image will be unsuccessful.
         free_image(self.handle, self.cbuf)

   def center(self):
      """Not supported by this camera"""
      pass

   def pan(self):
      """Not supported by this camera"""
      raise "Pan not supported"

   def tilt(self):
      """Not supported by this camera"""
      raise "Tilt not supported"

   def zoom(self):
      """Not supported by this camera"""
      raise "Zoom not supported"

   def saveAsTGA(self, path = "~/V4LGrab.tga"):
      """
      Save a copy of the image to disk, in TGA format (Gimp and display
      can read it).

      path is the name of the save file, and defaults to '~/V4LGrab.tga'
      """
      file = open(path, "w")
      file.write("\x00") #byte 0
      file.write("\x00") #byte 1
      if self.color:
         file.write("\x02") #type 2, uncompressed color
      else:
         file.write("\x03") #type 3, uncompressed greyscale
      file.write("\x00"*5) #Color Map (3-7); data is ignored
      file.write("\x00\x00") #X Origin
      file.write("\x00\x00") #Y Origin
      file.write("%c%c" % (self.width & 0xFF, self.width >> 8)) #Width
      file.write("%c%c" % (self.height & 0xFF, self.height >> 8)) #Height
      file.write("%c" % (self.depth*8)) #bpp
      file.write("\x20") #attributes
      file.write(self.cbuf)
      file.close

   def makeWindow(self):
      self.root = Tk()
      im = PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                               (self.width, self.height),
                                               self.cbuf, 'raw', "BGR")
      self.image = ImageTk.PhotoImage(im)
      label = Label(self.root, image=self.image, bd=0)
      label.pack({'fill':'both', 'expand':1, 'side': 'left'})
      while 1:
         im = PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                                  (self.width, self.height),
                                                  self.cbuf, 'raw', "BGR")
         self.image = ImageTk.PhotoImage(im)
         while self.root.tk.dooneevent(2): pass
         time.sleep(.5)
         print ".",
         sys.stdout.flush()
         self.update()

class CBuffer:
   """
   A private buffer class to transmute the CBuffer we get in V4LGrabber.data
   into something that looks like a Python list.
   """
   def __init__(self, cbuf):
      self.data = cbuf

   def __getitem__(self, key):
      if isinstance(key, types.SliceType):
         if key.stop > len(self):
            stop = len(self)
         else:
            stop = key.stop
         return struct.unpack("B" * (stop - key.start),
                            self.data[key.start:stop])
      else:
         return struct.unpack("B", self.data[key])[0]

   def __len__(self):
      return len(self.data)

   def __str__(self):
      return str(self[:])   

if __name__ == "__main__":
   cam = V4LGrabber(384, 240)

   if 0:
      cam.makeWindow()

   if 1:
      root = Tk()
      im = PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                               (cam.width, cam.height),
                                               cam.cbuf, 'raw', "BGR")
      image = ImageTk.PhotoImage(im)
      label = Label(root, image=image, bd=0)
      label.pack({'fill':'both', 'expand':1, 'side': 'left'})
      while 1:
         while root.tk.dooneevent(2): pass
         cam.update()
         im = PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                                  (cam.width, cam.height),
                                                  cam.cbuf, 'raw', "BGR")
         image = ImageTk.PhotoImage(im)
         label.configure(image = image)

   if 0:
      print "Testing frames per/second:",
      start = time.time()
      for i in range(100):
         print ".",
         sys.stdout.flush()
         cam.update()
      stop = time.time()
      print "done!"
      print "FPS = ", 100.00/ (stop - start)

   if 0:
      print "Saving images:"
      print "test1.tga..."
      cam.saveAsTGA("./test1.tga")
      time.sleep(3)
      print "test1.tga..."
      cam.saveAsTGA("./test2.tga")
      cam.update()
      print "test1.tga..."
      cam.saveAsTGA("./test3.tga")

      print """
      If everything worked, then test1.tga and test2.tga should be identical,
      but test3.tga should have been snapped about a second later.  They are
      all saved in the current directory.
      """
   if 0:
      print "Testing greyscale..."
      cam = V4LGrabber(384, 240, 1)
      cam.save("./testgrey.tga")
      print "Saved testgrey.tga"

   del cam

