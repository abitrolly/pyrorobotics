# A Base Camera class

from pyro.vision import *
from pyro.robot.service import Service

import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk

class Camera(PyroImage, Service):
   """
   A base class for Camera
   """
   def __init__(self, width, height, depth = 3):
      """
      To specify the resolution of a particular camera, overload this
      constructor with one that initalizes the dimensions itself
      """
      PyroImage.__init__(self, width, height, depth, 0)
      Service.__init__(self, 'camera')
      self.app = 0
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

   def getImage(self):
      raise "MethodNotDefined", "getImage()"

   def makeWindow(self):
      if self.app != 0:
         self.window.deiconify()
      else:
         self.app = Tkinter.Tk()
         self.app.withdraw()
         self.window = Tkinter.Toplevel()
         self.window.wm_title("Camera View")
         self.im = self.getImage()
         self.image = ImageTk.PhotoImage(self.im)
         self.label = Tkinter.Label(self.window, image=self.image, bd=0)
         self.label.pack({'fill':'both', 'expand':1, 'side': 'left'})
         self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
      self.visible = 1
      while self.window.tk.dooneevent(2): pass

   def hideWindow(self):
      self.visible = 0
      self.window.withdraw()
      
   def updateWindow(self):
      self.im = self.getImage()
      self.image = ImageTk.PhotoImage(self.im)
      self.label.configure(image = self.image)
      while self.window.tk.dooneevent(2): pass

   def startService(self):
      self.state = "started"
      return "Ok"

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

if __name__ == '__main__':
   from os import getenv
   mycam = Camera(0,0)
   mycam.loadFromFile(getenv('PYRO') + "/vision/snaps/som-21.ppm")      
