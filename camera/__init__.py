# A Base Camera class

from pyro.vision import *
from pyro.robot.service import Service

import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk, types

def listFilter(allArgs):
   print 'camera.apply("%s",' % allArgs[0],
   if len(allArgs) > 1:
      for a in allArgs[1]:
         print a, ",",
   print ")"

def makeArgList(item):
   if type(item) == type(""):
      return (item, )
   return (item[0], item[1:])

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
      self.filterMode = 1
      self.callback = None
      self.blob = [BlobData(width,height),BlobData(width,height),BlobData(width,height),BlobData(width,height),BlobData(width,height)]
      self.maxBlob = self.blob[0]

      # specific camera type will define self.rgb = (0, 1, 2) offsets
      # and self.format = "RGB", for example

      self.update() # call it once to initialize

   def setFilterList(self, filterList):
      """
      Filters take the form: ("name", (args))
      Example: cam.setFilterList([("superColor",1,-1,-1,0),("meanBlur",3)]) 
      """
      myList = map(makeArgList, filterList)
      self.vision.setFilterList(myList)
      # if paused, update the screen
      if not self.active:
         self.updateOnce()

   def popFilterList(self):
      self.vision.popFilterList()
      # if paused, update the screen
      if not self.active:
         self.updateOnce()

   def getFilterList(self):
      return self.vision.getFilterList()

   def loadFilters(self):
      pass

   def saveFilters(self):
      pass

   def maxBlobs(self, channel, low_threshold, high_threshold, sortMethod, number, drawBox=1):

      if(sortMethod.lower() == "mass"):
         method = 0

      elif(sortMethod.lower() =="area"):
         method = 1

      else:
         print "Invalid Sort Parameter to maxBlobs."

      if number == 1:
         self.maxBlob.min_x, self.maxBlob.min_y, self.maxBlob.max_x,self.maxBlob.max_y, self.maxBlob.mass = self.vision.blobify( channel,low_threshold,high_threshold,method,number,drawBox);

      elif number == 2:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass = self.vision.blobify(channel,low_threshold,high_threshold,method,number,drawBox);
               
      elif number == 3:
         self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass = self.vision.blobify(channel,low_threshold,high_threshold,method,number,drawBox);

      elif number == 4:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass,self.blob[3].min_x,self.blob[3].min_y,self.blob[3].max_x,self.blob[3].max_y,self.blob[3].mass = self.vision.blobify(channel,low_threshold,high_threshold,method,number,drawBox);

      elif number == 5:
               self.blob[0].min_x,self.blob[0].min_y,self.blob[0].max_x,self.blob[0].max_y,self.blob[0].mass,self.blob[1].min_x,self.blob[1].min_y,self.blob[1].max_x,self.blob[1].max_y,self.blob[1].mass,self.blob[2].min_x,self.blob[2].min_y,self.blob[2].max_x,self.blob[2].max_y,self.blob[2].mass,self.blob[3].min_x,self.blob[3].min_y,self.blob[3].max_x,self.blob[3].max_y,self.blob[3].mass,self.blob[4].min_x,self.blob[4].min_y,self.blob[4].max_x,self.blob[4].max_y,self.blob[4].mass = self.vision.blobify(channel,low_threshold,high_threshold,method,number,drawBox);

      else:
         print "Invalid parameter to maxBlobs: number, must be 1-5"

      #not good, 1 pixel is very dense.
      #elif(cmp(sortMethod.lower(),"density")==0):
      #   self.min_x, self.min_y,self.max_x,self.max_y,self.mass = blobify(channel, low_threshold,high_threshold,2,drawBox,self.width, self.height);

   def superColorByName(self, color, channel):

      if(channel < 0 or channel > 3):
         print "Invalid Color Channel to Super Color"
         return;

      if (color.lower() == "red"):
         self.vision.superColor(1, -1, -1, channel)
      elif (color.lower() == "green"):
         self.vision.superColor(-1, 1, -1, channel)
      elif (color.lower() == "blue"):
         self.vision.superColor(-1, -1, 1, channel)
      # fix the following; they need fractional weights:
      elif (color.lower() == "magenta"):
         self.vision.superColor(1, -1, 0.5, channel)
      elif (color.lower() == "yellow"):
         self.vision.superColor(1.0/6.0, 2.0/6.0, -1, channel)
      elif (color.lower() == "cyan"):
         self.vision.superColor(-1, 1/2.0, 1/2.0, channel)
      else:
         print "Invalid Super Color"
         
   def trainColor(self):
      self.histogram = self.vision.Hist()
      self.histogram.red, self.histogram.green, self.histogram.blue = self.vision.trainColor();

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

   def updateOnce(self):
      self.active = 1
      self.update()
      self.active = 0

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
         w, h = self.width, self.height
         while w < 200:
            w, h = map(lambda x: x * 2, (w, h))
         self.canvas = Tkinter.Canvas(self.window, width = w, height = h)
         self.canvas.pack({'fill':'both', 'expand':1, 'side': 'bottom'})
         self.canvas.bind("<1>", self.processLeftClick)
         #self.canvas.bind("<Enter>", self.togglePlay)
         #self.canvas.focus_set()
         self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
         menu = [('File',[['Load Filters...',self.loadFilters],
                          ['Save Filters...', self.saveFilters],
                          None,
                          ['Close',self.hideWindow] 
                          ]),
                 ('View', [['Pause', lambda self=self: self.setActive(0)],
                           ['Play', lambda self=self: self.setActive(1)],
                           ['Update', lambda self=self: self.updateOnce()],
                           ]),
                 ('Filter', [['List filters', self.listFilterList],
                             ['Toggle filter mode', self.toggleFilterMode],
                             None,
                             ['Clear last filter', self.popFilterList],
                             ['Clear all filters', lambda self=self: self.setFilterList( [] )],
                             ['Clear callback function', lambda self=self: self.setCallback( None )],
                             ]),
                 ('Add', [['blur edges', lambda self=self: self.addFilter( "meanBlur") ],
                          ['detect edges', lambda self=self: self.addFilter( "sobel") ],
                          ['gray scale', lambda self=self: self.addFilter("grayScale")],
                          None,
                          ['blobify red', lambda self=self: self.addFilter("blobify", 0, 255, 255, 0, 1, 1)],
                          ['blobify green', lambda self=self: self.addFilter("blobify", 1, 255, 255, 0, 1, 1)],
                          ['blobify blue', lambda self=self: self.addFilter("blobify", 2, 255, 255, 0, 1, 1)],
                          None,
                          ['clear red', lambda self=self: self.addFilter("setPlane", 0)],
                          ['clear green', lambda self=self: self.addFilter("setPlane", 1)],
                          ['clear blue', lambda self=self: self.addFilter("setPlane", 2)],
                          None,
                          ['superColor red', lambda self=self: self.addFilter("superColor", 1, -1, -1, 0)],
                          ['superColor green', lambda self=self: self.addFilter("superColor", -1, 1, -1, 1)],
                          ['superColor blue', lambda self=self: self.addFilter("superColor", -1, -1, 1, 2)],
                          None,
                          ['threshold red', lambda self=self: self.addFilter("threshold", 0)],
                          ['threshold green', lambda self=self: self.addFilter("threshold", 1)],
                          ['threshold blue', lambda self=self: self.addFilter("threshold", 2)],
                          None,
                          ['inverse red', lambda self=self: self.addFilter("inverse", 0)],
                          ['inverse green', lambda self=self: self.addFilter("inverse", 1)],
                          ['inverse blue', lambda self=self: self.addFilter("inverse", 2)],
                          
                          ]),
                 ]
         # create menu
         self.mBar = Tkinter.Frame(self.window, relief=Tkinter.RAISED, borderwidth=2)
         self.mBar.pack(fill=Tkinter.X, side = "top")
         self.goButtons = {}
         self.menuButtons = {}
         for entry in menu:
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))
         
      self.visible = 1
      while self.window.tk.dooneevent(2): pass

   def apply(self, command, *args):
      if type(command) == type(""):
         return self.vision.applyFilters( [(command, args)] )
      else:
         raise "Improper format for apply()"

   def addFilter(self, command, *args):
      """
      Add a filter to the filter list.
      Example: cam.addFilter( "superColor", 3)
      """
      self.vision.addFilter( (command, args) )
      #listFilter( (command, args) )
      if not self.active:
         # if paused, apply it once, and update
         #Camera.__dict__[command](self, *args)
         self.vision.applyFilters( [(command, args)] )

   def setActive(self, val):
      self.active = val

   def makeMenu(self, bar, name, commands):
      """ Assumes self.menuButtons exists """
      menu = Tkinter.Menubutton(bar,text=name,underline=0)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         if cmd:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
         else:
            menu.filemenu.add_separator()
      menu['menu'] = menu.filemenu
      return menu

   def listFilterList(self):
      print "Filters:"
      map(listFilter, self.vision.getFilterList())

   def togglePlay(self, event):
      self.active = not self.active

   def toggleFilterMode(self):
      self.filterMode = not self.filterMode
      if not self.active:
         self.updateOnce()

   def processLeftClick(self, event):
      x, y = event.x/float(self.window.winfo_width()), event.y/float(self.window.winfo_height())
      x, y = x * self.width, y * self.height
      rgb = self.vision.get(int(x), int(y))
      self.addFilter("match", rgb[0], rgb[1], rgb[2]) 

   def hideWindow(self):
      self.visible = 0
      self.window.withdraw()
      
   def updateWindow(self):
      self.canvas.delete("image")
      self.im = self.getImage()
      try:
         self.im = self.im.resize( (self.window.winfo_width() - 2, 
                                    self.window.winfo_height() - 2) )
         #Image.BILINEAR ) # too slow
      except:
         print "error: could not resize window"         
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

   def setCallback(self, callback):
      # callback is a function that has first param
      # as self (ie, the visionSystem object)
      self.callback = callback
      if self.active == 0:
         self.update()

   def processAll(self):
      if self.filterMode:
         self.vision.applyFilterList()
         if self.callback:
            self.callback(self)

if __name__ == '__main__':
   cam = Camera(100, 80)
   cam.makeWindow()
   cam.mainloop()
