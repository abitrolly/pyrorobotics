from pyro.camera import *
from pyro.brain.behaviors.core import sleep
from grabImage import *
from UserString import UserString
import types
import sys, os

import PIL.PpmImagePlugin
import time
import re


class BlobData:
   def __init__(self, width, height):
      self.min_x = width
      self.min_y = height
      self.max_x = 0
      self.max_y = 0
      self.mass = 0
   
class Hist:
   def __init__(self):
      self.red = 0
      self.green = 0
      self.blue = 0
      

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
   def __init__(self, width, height, depth = 3,
                device = '/dev/video0', channel = 1):
      """
      Currently, if depth is any number other than 1 or 3, an exception
      will be raised.  I plan on implementing various color depths soon.

      Device should be the name of the capture device in the /dev directory.
      This is highly machine- and configuration-dependent, so make sure you
      know what works on your system
      
      Channel -  0: television; 1: composite; 2: S-Video
      """
      if depth == 1:
         self.color = 0
      elif depth == 3:
         self.color = 1
      else:
         raise ValueError, "unsupported color depth: %d" % self.depth
      if width < 48:
         raise ValueError, "width must be greater than 48"
      if height < 48:
         raise ValueError, "height must be greater than 48"
      self.device = device
      self.handle=None
      self.cbuf=None
      try:
         self.size, self.depth, self.handle, self.cbuf = \
                    grab_image(device, width, height, self.color, channel)
      except:
         print "v4l: grab_image failed!"
      Camera.__init__(self, width, height, depth)
      self.rgb = (2, 1, 0) # offsets to BGR
      self.data = CBuffer(self.cbuf)


      # lockCamera is used for processing in place -- if 0, refresh_image
      # will update the image; if 1, processing is occuring on the
      # buffer, so refresh_image will not update
      self.lockCamera = 0

      # puts a sleep in the update function to slow down video
      # to beable to see the video screen update.
      # sleeptime tells how long to sleep for.
      self.sleepFlag = 0
      self.sleepTime = 2

      self.blob = [BlobData(width,height),BlobData(width,height),BlobData(width,height),BlobData(width,height),BlobData(width,height)]
      self.maxBlob = self.blob[0]

   def _update(self):
      """
      Since data is mmaped to the capture card, all we have to do is call
      refresh.
      """
      try:
         refresh_image(self.handle, self.width, self.height, self.depth*8)
      except:
         print "v4l: refresh_image failed"

   def saveImage(self, filename="image.ppm"):
      save_image(self.width, self.height, filename)      


   def colorFilterOneTol(self, red, green, blue, tol=30, channel=1):
      color_filter(red-tol, green-tol, blue-tol,
                   red+tol, green+tol, blue+tol,
                   channel, self.width, self.height)
      self.sleepCheck()
      

   def colorFilterThreeTol(self, red, green, blue, t1=30,t2=30,t3=30, channel=1):
      color_filter(red-t1, green-t2, blue-t3,
                   red+t1, green+t2, blue+t3,
                   channel, self.width, self.height)
      self.sleepCheck();



   def colorFilterHiLow(self, lred, hred, lgreen,
                        hgreen, lblue,hblue, channel=1):
      color_filter(lred, lgreen, lblue,hred, hgreen, hblue,
                   channel,self.width, self.height)
      self.sleepCheck();



   def maxBlobs(self, channel, low_threshold, high_threshold, sortMethod, number, drawBox=1):

      if(cmp(sortMethod.lower(),"mass")==0):
         method = 0

      elif(cmp(sortMethod.lower(),"area")==0):
         method = 1

      else:
         print "Invalid Sort Parameter to maxBlobs."

      if number == 1:
         self.maxBlob.min_x, self.maxBlob.min_y, self.maxBlob.max_x,self.maxBlob.max_y, self.maxBlob.mass = blobify( channel,low_threshold,high_threshold,method,number,drawBox,self.width,self.height);

      elif number == 2:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass = blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);
               
      elif number == 3:
         self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass = blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);

      elif number == 4:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass,self.blob[3].min_x,self.blob[3].min_y,self.blob[3].max_x,self.blob[3].max_y,self.blob[3].mass = blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);

      elif number == 5:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass,self.blob[3].min_x,self.blob[3].min_y,self.blob[3].max_x,self.blob[3].max_y,self.blob[3].mass,self.blob[4].min_x,self.blob[4].min_y,self.blob[4].max_x,self.blob[4].max_y,self.blob[4].mass = blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);

      else:
         print "Invalid parameter to maxBlobs: number, must be 1-5"

      #not good, 1 pixel is very dense.
      #elif(cmp(sortMethod.lower(),"density")==0):
      #   self.min_x, self.min_y,self.max_x,self.max_y,self.mass = blobify(channel, low_threshold,high_threshold,2,drawBox,self.width, self.height);

      self.sleepCheck();


   def meanBlur(self, kernel=3):
      mean_blur(kernel, self.width, self.height)
      self.sleepCheck()

   def medianBlur(self, kernel = 3):
      median_blur(kernel, self.width, self.height)
      self.sleepCheck()
   

   def superColor(self, color, channel, lighten=0):

      if(channel < 0 or channel > 3):
         print "Invalid Color Channel to Super Color"
         return;

      #incoming is RGB, Buffer is BGR
      if(channel == 0):
         channel = 2
      elif(channel == 2):
         channel = 0;

      if(cmp(color.lower(), "red") == 0):
         super_red(channel,lighten,self.width,self.height)
      elif(cmp(color.lower(), "green") == 0):
         super_green(channel,lighten,self.width,self.height)
      elif(cmp(color.lower(), "blue") == 0):
         super_blue(channel,lighten,self.width,self.height)
##       elif(cmp(color.lower(), "magenta") == 0):
##          print "in super magenta"
##          super_magenta(channel,lighten,self.width,self.height)
##       elif(cmp(color.lower(), "yellow") == 0):
##          print "in super yellow"
##          super_yellow(channel,lighten,self.width,self.height)
##       elif(cmp(color.lower(), "cyan") == 0):
##          print "in super cyan"         
##          super_cyan(channel,lighten,self.width,self.height)      
      else:
         print "Invalid Super Color"
         
      self.sleepCheck()


   def gaussianBlur(self):
      gaussian_blur(self.width, self.height)
      self.sleepCheck()

   def edgeDetection(self):
      sobel(1, self.width, self.height)
      self.sleepCheck()

   def toGreyScale(self):
      grey_scale(3, self.width, self.height)
      self.sleepCheck()

   def sleepCheck(self):
      if(self.sleepFlag):
         sleep(self.sleepTime)


   def trainColor(self):
      self.histogram = Hist()
      self.histogram.red, self.histogram.green, self.histogram.blue = train_color(self.width,
                                                                                  self.height);


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

   def getImage(self):
      return PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                                 (self.width, self.height),
                                                 self.cbuf, 'raw', "BGR")
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

   def __setitem__(self, key, value):
      if isinstance(key, types.SliceType):
         if key.stop > len(self):
            stop = len(self)
         else:
            stop = key.stop
         return struct.unpack("B" * (stop - key.start),
                            self.data[key.start:stop])
      else:
         # FIX: can't do this from Python, need C function
         self.data[key] = struct.pack("B", value)

   def __len__(self):
      return len(self.data)

   def __str__(self):
      return str(self[:])   



class FakeCamera(V4LGrabber):
   """
   A fake camera.  This will emulate a V4LGrabber, but instead of
   accessing the hardware, it will load a series of images from file.
   """
   def __init__(self, pattern, start = 0, limit = -1, char = "?"):
      """
      pattern is a filename with indicators on where to put digits for the
      sequence.  Absolute or relative filenames can be used.
      For example, 'image???-.ppm' would start at 'image000.ppm'
      and continue up to limit.
      char is the character that should be replaced in the pattern.

      As an example, to load image000.ppm through image120.ppm, we could call
      FakeCamera('imagexxx.ppm', 0, 120, 'x')
      """
      self.pattern = pattern
      self.limit = limit
      #create a matchdata object that we will store
      self.match = re.search(re.escape(char) + "+", pattern)
      #create a format string that we can use to replace the
      #replace characters
      self.fstring = "%%0%dd" % len(self.match.group())
      self.current = start
      currname = self.pattern[:self.match.start()] + \
                 self.fstring % self.current + \
                 self.pattern[self.match.end():]
      self.width, self.height, self.depth, self.cbuf = fake_grab_image(currname)
      if self.depth == 8:
         self.color = 0
      else:
         self.color = 1
         
      Camera.__init__(self, self.width, self.height, self.depth)
      self.data = CBuffer(self.cbuf)

      #for compatibility with V4LGrabber fucntions
      self.lockCamera = 0
      self.rgb = (0, 1, 2) # offsets to BGR
      

      # puts a sleep in the update function to slow down video
      # to beable to see the video screen update.
      # sleeptime tells how long to sleep for.
      self.sleepFlag = 0
      self.sleepTime = 2
      
      self.min_x = width
      self.min_y = height
      self.max_x = 0
      self.max_y = 0
      #self.cm_x = 0
      #self.cm_y = 0
      self.mass  = 0
      
   def _update(self):
      if self.limit > 0:
         if (self.current < self.limit):
            currname = self.pattern[:self.match.start()] + \
                       self.fstring % self.current + \
                       self.pattern[self.match.end():]
            fake_load_image(currname)
            self.current += 1

   def __del__(self):
      fake_free_image()



if __name__ == "__main__":
   cam = V4LGrabber(384, 240)

   if 1:
      cam.makeWindow()
      while 1:
         cam.updateWindow()

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

