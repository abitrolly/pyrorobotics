from pyro.camera import *
from grabImage import *
from UserString import UserString
import types
import sys

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

      self.width = width
      self.height = height
      
      self.device = device
      #handle is the file handle for device
      #it needs to get passed back to refresh
      #and free
      self.size, self.depth, self.handle, self.cbuf = \
                 grab_image(device, width, height, self.color)
      self.data = CBuffer(self.cbuf)

   def _update(self):
      """
      Since data is mmaped to the capture card, all we have to do is call
      refresh.
      """
      refresh_image(self.handle, self.width, self.height, self.depth)

   def __del__(self):
      """
      DO NOT REMOVE THIS!
      This deconstructor method makes sure that the mmap is freed before the
      Camera is deleted.
      """
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

   def save(self, path = "~/V4LGrab.tga"):
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
         file.write("\x03") #type 3, uncompress greyscale
      file.write("xxxxx") #Color Map (3-7); data is ignored
      file.write("\x00\x00") #X Origin
      file.write("\x00\x00") #Y Origin
      file.write("%c%c" % (self.width & 0xFF, self.width >> 8)) #Width
      file.write("%c%c" % (self.height & 0xFF, self.height >> 8)) #Height
      file.write("%c" % (self.depth)) #bpp
      file.write("\x20") #attributes
      file.write(self.cbuf)
      file.close

class CBuffer:
   """
   A private buffer class to transmute the CBuffer we get in V4LGrabber.data
   into something that looks like a Python list.
   """
   def __init__(self, cbuf):
      self.data = cbuf

   def __getitem__(self, key):
      if isinstance(key, types.SliceType):
         if key.stop == sys.maxint:
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
   from grabImage import *
   from pyro.camera.v4l import *
   import time

   #print "Opening the camera directly using the C interface..."
   #image = grab_image("/dev/video0", 384, 240)

   #print "Printing the first 10 bytes..."
   #for x in range(10):
   #   print "%X" % (image[x])

   #print "Freeing..."
   #free_image(image)

   print "Now using the V4LGrabber class..."
   cam = V4LGrabber(384, 240)
   #cam.update()
   cam.save("./test1.tga")
   time.sleep(3)
   cam.save("./test2.tga")
   cam.update()
   cam.save("./test3.tga")

   print """
   If everything worked, then test1.tga and test2.tga should be identical,
   but test3.tga should have been snapped about a second later.  They are
   all saved in the current directory.
   """
   del cam
   time.sleep(.5)


   #print "Testing greyscale..."
   #cam = V4LGrabber(384, 240, 1)
   #cam.save("./testgrey.tga")
   #print "Saved testgrey.tga"
   


      


   
