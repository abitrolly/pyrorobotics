# A Base Camera class

from pyro.vision import PyroImage
from pyro.robot.service import Service

import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk, types, time, struct

def display(item):
   print item

def listFilter(allArgs):
   retval = 'camera.apply("%s",' % allArgs[0]
   if len(allArgs) > 1:
      for a in allArgs[1]:
         retval += str(a) + ","
   return retval + ")"

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
      #PyroImage.__init__(self, width, height, depth, 0)
      Service.__init__(self, 'camera')
      self.app = 0
      self.title = title
      self.filterMode = 1
      self.callbackList = []
      self.filterReturnValue = []
      self.callbackTextList = []
      # specific camera type will define self.rgb = (0, 1, 2) offsets
      # and self.format = "RGB", for example
      self.lastWindowUpdate = 0
      self.updateWindowInterval = 1.0 # update window once a second
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

   def getData(self):
      data = [0 for y in range(self.height * self.width * self.depth)]
      for x in range(self.width):
         for y in range(self.height):
            rgb = self.getVal(x, y)
            data[(x + y * self.width) * self.depth + 0] = rgb[self.rgb[0]]
            data[(x + y * self.width) * self.depth + 1] = rgb[self.rgb[1]]
            data[(x + y * self.width) * self.depth + 2] = rgb[self.rgb[2]]
      return data

   def saveImage(self, filename = "pyro-vision.ppm"):
      self.vision.saveImage(filename);

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
                       (self.vision.get(x, y) / 3.0)) > threshold):
                  self.motion.set(x, y, 1)
                  self.movedPixelCount += 1
         print "moved:", self.movedPixelCount

   def updateOnce(self):
      oldActive = self.active
      self.active = 1
      self.update()
      self.processAll()
      self.active = oldActive

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
         #while w < 310:
         #   w, h = map(lambda x: x * 2, (w, h))
         self.canvas = Tkinter.Canvas(self.window, width = w, height = h)
         self.canvas.pack({'fill': 'both', 'expand': 'y', 'side': 'bottom'})
         self.canvas.bind("<Button-1>", self.processLeftClickDown)
         self.canvas.bind("<ButtonRelease-1>", self.processLeftClickUp)
         #self.canvas.bind("<Enter>", self.togglePlay)
         #self.canvas.focus_set()
         self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
         menu = [('File',[['Load Filters...',self.loadFilters],
                          ['Save Filters...', self.saveFilters],
                          None,
                          ['Save Image...', self.saveImage],
                          None,
                          ['Close',self.hideWindow] 
                          ]),
                 ('View', [['Pause', lambda self=self: self.setActive(0)],
                           ['Play', lambda self=self: self.setActive(1)],
                           ['Update', lambda self=self: self.updateOnce()],
                           ]),
                 ('Filter', [['List filters', self.listCallbackList],
                             ['Toggle filter mode', self.toggleFilterMode],
                             None,
                             ['Clear last filter', self.popCallbackList],
                             ['Clear all filters', lambda self=self: self.clearCallbackList( )],
                             ]),
                 ('Add', [['meanBlur', lambda self=self: self.addFilter( "meanBlur") ],
                          ['gaussianBlur', lambda self=self: self.addFilter( "gaussianBlur") ],
                          ['medianBlur', lambda self=self: self.addFilter( "medianBlur") ],
                          ['sobel (detect edges)', lambda self=self: self.addFilter( "sobel") ],
                          ['scale', lambda self=self: self.addFilter("scale", 1.5)],
                          ['gray scale', lambda self=self: self.addFilter("grayScale")],
                          ['backup', lambda self=self: self.addFilter("backup")],
                          ['restore', lambda self=self: self.addFilter("restore")],
                          ['motion', lambda self=self: self.addFilter("motion")],
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
         self.mBar.pack(fill=Tkinter.X, expand='n', side = "top")
         self.goButtons = {}
         self.menuButtons = {}
         for entry in menu:
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))
         
      self.visible = 1
      self.window.aspect(self.width, self.height, self.width, self.height)
      #self.window.minsize(355, 0)
      while self.window.tk.dooneevent(2): pass

   def apply(self, command, *args):
      if type(command) == type(""):
         return self.vision.applyFilter( (command, args) )
      else:
         raise "Improper format for apply()"

   def addFilter(self, func, *args):
      """
      Add a filter to the filter list.
      Example: cam.addFilter( "superColor", 3)
      """
      import inspect
      if type(func) == type(""):
         self.callbackList.append( lambda self=self, func=func, args=args: self.apply(func, *args))
         self.callbackTextList.append( listFilter( (func, args) ))
      else:
         self.callbackList.append( func )
         try:
            self.callbackTextList.append( inspect.getsource( func ))
         except:
            self.callbackTextList.append( "[User Defined Function]" )
      if not self.active:
         # if paused, apply it once, and update
         self.processAll()
      return len(self.callbackList) - 1

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

   def listCallbackList(self):
      print "Filters:"
      map(display, self.callbackTextList)

   def togglePlay(self, event):
      self.active = not self.active

   def toggleFilterMode(self):
      self.filterMode = not self.filterMode
      if not self.active:
         self.updateOnce()

   def processLeftClickDown(self, event):
      x, y = event.x/float(self.window.winfo_width()), event.y/float(self.window.winfo_height())
      self.lastX, self.lastY = int(x * self.width), int(y * self.height)

#    def get(self, x, y, offset = 0):
#       """
#       Get a pixel value. offset is r, g, b = 0, 1, 2.
#       """
#       rgb = self.vision.get(int(x), int(y))
#       return rgb[offset]

#    def getVal(self, x, y):
#       return self.vision.get(int(x), int(y))

#    def getRow(self, y):
#       """ Get the entire row, in tuples """
#       retval = [0] * self.width
#       for x in range(self.width):
#          retval[x] = self.getVal(x, y)
#       return retval

#    def getDim(self):
#       return self.width, self.height

#    def getCol(self, x):
#       """ Get the entire col, in tuples """
#       retval = [0] * self.height
#       for y in range(self.height):
#          retval[y] = self.getVal(x, y)
#       return retval


   def processLeftClickUp(self, event):
      x, y = event.x/float(self.window.winfo_width()), event.y/float(self.window.winfo_height())
      x, y = int(x * self.width), int(y * self.height)
      if (x == self.lastX and y == self.lastY):
         rgb = self.vision.get(int(x), int(y))
         print 'camera.addFilter("match", %d, %d, %d)' % (rgb[0], rgb[1], rgb[2])
         return self.addFilter("match", rgb[0], rgb[1], rgb[2])
      else:
         print 'camera.addFilter("histogram", %d, %d, %d, %d, 8)' % (self.lastX, self.lastY, x, y)
         return self.addFilter("histogram", self.lastX, self.lastY, x, y, 8)

   def hideWindow(self):
      self.visible = 0
      self.window.withdraw()
      
   def updateWindow(self):
      now = time.time()
      if now - self.lastWindowUpdate < self.updateWindowInterval:
         return
      self.lastWindowUpdate = now
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

   def delFilter(self, pos):
      self.callbackList.remove(pos)
      self.callbackTextList.remove(pos)
      if not self.active:
         self.updateOnce()
      return "Ok"

   def popCallbackList(self):
      if len(self.callbackList) > 0:
         self.callbackList.pop()
         self.callbackTextList.pop()
      if not self.active:
         self.updateOnce()
      return "Ok"

   def clearCallbackList(self):
      # callback is a function that has first param
      # as self (ie, the visionSystem object)
      self.callbackList = []
      self.callbackTextList = []
      if not self.active:
         self.updateOnce()
      return "Ok"

   def processAll(self):
      if self.filterMode:
         self.vision.applyFilterList()
         self.filterReturnValue = []
         for filterFunc in self.callbackList:
            self.filterReturnValue.append( filterFunc(self) )

if __name__ == '__main__':
   cam = Camera(100, 80)
   cam.visionSystem = FakeVisionSystem()
   cam.makeWindow()
   cam.window.mainloop()
