# A Base Camera class

import pyro.system.share as share
from pyro.vision import *
from pyro.robot.service import Service

import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk, types

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

class CBuffer:
   """
   A private buffer class to transmute the CBuffer we get in data
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

class Camera(PyroImage, Service):
   """
   A base class for Camera
   """
   def __init__(self, width, height, depth = 3, title = "Camera View"):
      """
      To specify the resolution of a particular camera, overload this
      constructor with one that initalizes the dimensions itself
      """
      PyroImage.__init__(self, width, height, depth, 0)
      Service.__init__(self, 'camera')
      self.app = 0
      self.title = title

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

      # specific camera type will define self.rgb = (0, 1, 2) offsets
      # and self.format = "RGB", for example

      self.update() # call it once to initialize

   def saveImage(self, filename="image.ppm"):
      self.cobj.saveImage(filename)      

   def colorFilterOneTol(self, red, green, blue, tol=30, channel=1):
      self.cobj.filterByColor(red, green, blue, tol, channel)
      self.sleepCheck()
      
   def colorFilterThreeTol(self, red, green, blue, t1=30,t2=30,t3=30, channel=1):
      self.cobj.filterByColor(red-t1, green-t2, blue-t3,
                                    red+t1, green+t2, blue+t3,
                                    channel)
      self.sleepCheck();

   def colorFilterHiLow(self, lred, hred, lgreen,
                        hgreen, lblue,hblue, channel=1):
      self.cobj.filterByColor(lred, lgreen, lblue, hred, hgreen, hblue,
                              channel)
      self.sleepCheck();


   def maxBlobs(self, channel, low_threshold, high_threshold, sortMethod, number, drawBox=1):

      if(cmp(self.cobj.sortMethod.lower(),"mass")==0):
         method = 0

      elif(cmp(self.cobj.sortMethod.lower(),"area")==0):
         method = 1

      else:
         print "Invalid Sort Parameter to maxBlobs."

      if number == 1:
         self.maxBlob.min_x, self.maxBlob.min_y, self.maxBlob.max_x,self.maxBlob.max_y, self.maxBlob.mass = self.cobj.blobify( channel,low_threshold,high_threshold,method,number,drawBox,self.width,self.height);

      elif number == 2:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass = self.cobj.blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);
               
      elif number == 3:
         self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass = self.cobj.blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);

      elif number == 4:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass,self.blob[3].min_x,self.blob[3].min_y,self.blob[3].max_x,self.blob[3].max_y,self.blob[3].mass = self.cobj.blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);

      elif number == 5:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass,self.blob[3].min_x,self.blob[3].min_y,self.blob[3].max_x,self.blob[3].max_y,self.blob[3].mass,self.blob[4].min_x,self.blob[4].min_y,self.blob[4].max_x,self.blob[4].max_y,self.blob[4].mass = self.cobj.blobify(channel,low_threshold,high_threshold,method,number,drawBox,self.width, self.height);

      else:
         print "Invalid parameter to maxBlobs: number, must be 1-5"

      #not good, 1 pixel is very dense.
      #elif(cmp(sortMethod.lower(),"density")==0):
      #   self.min_x, self.min_y,self.max_x,self.max_y,self.mass = blobify(channel, low_threshold,high_threshold,2,drawBox,self.width, self.height);

      self.sleepCheck();


   def meanBlur(self, kernel=3):
      self.cobj.meanBlur(kernel)
      self.sleepCheck()

   def medianBlur(self, kernel = 3):
      self.cobj.medianBlur(kernel)
      self.sleepCheck()
   
   def superColor(self, color, channel):

      if(channel < 0 or channel > 3):
         print "Invalid Color Channel to Super Color"
         return;

      if (color.lower() == "red"):
         self.cobj.superColor(1, -1, -1, channel)
      elif (color.lower() == "green"):
         self.cobj.superColor(-1, 1, -1, channel)
      elif (color.lower() == "blue"):
         self.cobj.superColor(-1, -1, 1, channel)
      # fix the following; they need fractional weights:
      elif (color.lower() == "magenta"):
         self.cobj.superColor(-1, -1, 1, channel)
      elif (color.lower() == "yellow"):
         self.cobj.superColor(-1, -1, 1, channel)
      elif (color.lower() == "cyan"):
         self.cobj.superColor(-1, -1, 1, channel)
      else:
         print "Invalid Super Color"
         
      self.sleepCheck()

   def gaussianBlur(self):
      self.cobj.gaussianBlur()
      self.sleepCheck()

   def edgeDetection(self):
      self.cobj.sobel(1)
      self.sleepCheck()

   def toGreyScale(self):
      self.cobj.greyScale(3)
      self.sleepCheck()

   def sleepCheck(self):
      if(self.sleepFlag):
         sleep(self.sleepTime)

   def trainColor(self):
      self.histogram = self.cobj.Hist()
      self.histogram.red, self.histogram.green, self.histogram.blue = self.cobj.trainColor();


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

   def getImage(self):
      return PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                                 (self.width, self.height),
                                                 self.cbuf, 'raw', self.format)

   def makeWindow(self):
      if self.app != 0:
         self.window.deiconify()
      else:
         self.app = Tkinter.Tk()
         self.app.withdraw()
         self.window = Tkinter.Toplevel()
         self.window.wm_title(self.title)
         self.canvas = Tkinter.Canvas(self.window)
         self.canvas.pack({'fill':'both', 'expand':1, 'side': 'left'})
         self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
      self.visible = 1
      while self.window.tk.dooneevent(2): pass

   def hideWindow(self):
      self.visible = 0
      self.window.withdraw()
      
   def updateWindow(self):
      self.canvas.delete("image")
      self.im = self.getImage()
      self.im = self.im.resize( (self.window.winfo_width() - 2, 
                                 self.window.winfo_height() - 2),
                                Image.BILINEAR )
      self.image = ImageTk.PhotoImage(self.im)
      self.canvas.create_image(0, 0, image = self.image, anchor=Tkinter.NW,
                               tag="image")
      self.canvas.create_rectangle(1, 1,
                                   self.window.winfo_width() - 2,
                                   self.window.winfo_height() - 2, tag="image")
      self.canvas.pack()
      while self.window.tk.dooneevent(2): pass

   def startService(self):
      self.state = "started"
      return self

   def stopService(self):
      self.state = "stopped"
      self.visible = 0
      return "Ok"

   def getServiceData(self):
      return self.data

   def getServiceState(self):
      return self.state

   def updateService(self):
      self.update()
