#A set of model vector visualization tools.
#Each visualizer should be a subclass of VisVector, which is an abstract class.
#If a visualizer is added, it should be added to the if statement in
#VisVectorFactory.  Each new class should follow the nameing convention
#XVisVector, where X is the string that gets passed to VisVectorFactory

from pyro.brain.psom import *
from Tkinter import *
import struct
import ImageTk

class VisVector:
   """
   This is an abstract base class for a set of vector visualizers.
   Each subclass should be made specifically for a type of vector.
   """

   def __init__(self, vector, title=""):
      raise "This is an abstract function."

   def close(self):
      """Close my Window"""
      self.win.destroy()

class IRVisVector(VisVector):
   """
   Display a vector representing a list of IR sensor values as
   floats.
   """

   def __init__(self, vector, title=""):
      self.vector = vector.get_elts()
      self.length = len(self.vector)

      self.win = Tk()
      self.win.title(title)
      Lframe = Frame(self.win)
      Rframe = Frame(self.win)
      b = Button(self.win, text="Close", command=self.close)
      b.pack(side=BOTTOM)
      Lframe.pack(side=LEFT, fill=Y)
      Rframe.pack(side=RIGHT, fill=Y)
      for i in range(self.length):
         ll = Label(Lframe, text="IR" + str(i))
         ll.pack(anchor=W)
         rl = Label(Rframe, text="= " + str(self.vector[i]))
         rl.pack(anchor=W)

class GenericVisVector(VisVector):
   """
   Display a generic vector of floats.
   """
   def __init__(self, vector, title=""):
      self.vector = vector.get_elts()
      self.length = len(self.vector)

      self.win = Tk()
      self.win.title(title)
      Lframe = Frame(self.win)
      Rframe = Frame(self.win)
      b = Button(self.win, text="Close", command=self.close)
      b.pack(side=BOTTOM)
      Lframe.pack(side=LEFT, fill=Y)
      Rframe.pack(side=RIGHT, fill=Y)
      for i in range(self.length):
         ll = Label(Lframe, text=str(i))
         ll.pack(anchor=W)
         rl = Label(Rframe, text="= " + str(self.vector[i]))
         rl.pack(anchor=W)

class GrayscaleVisVector(VisVector):
   """
   Display a vector of floats representing a grayscale image
   """
   def __init__(self, vector, height, width, title=""):
      self.vector = vector.get_elts()
      self.length = len(self.vector)

      self.win = Tk()
      self.win.title(title)
      self.canvas = Canvas(self.win, width=width, height=height)
      self.canvas.pack()

      #turn unit-valued floats into 8-bit grayscale values...
      grayvec = map(lambda x: struct.pack("B", int(x*255)), self.vector)
      #...and pack them into a string.
      self.graystr = ""
      for pix in grayvec:
         self.graystr += pix
         
      img = ImageTk.Image.fromstring("L", (width, height), self.graystr)
      photo = ImageTk.PhotoImage(img)
      i = self.canvas.create_image(1,1,anchor=NW,image=photo)
      b = Button(self.win, text="Close", command=self.close)
      b.pack(side=BOTTOM)
      self.win.mainloop()

def getVisVectorByName(type):
   """
   Given a type of VisVector as a string, create and initialize an
   instance of that type, and return a reference.
   """
   if type == "IR":
      return IRVisVector
   elif type == "Generic":
      return GenericVisVector
   elif type =="Grayscale" or type =="Greyscale":
      return GrayscaleVisVector
   else:
      raise "VisVector type not supported"

if __name__=="__main__":
   from pyro.brain.psom import *
   grayvis = getVisVectorByName("Grayscale")
   piclist = [float(x)/255.0 for x in range(256)]
   grayvis(vector(piclist), 16, 16)
   print "Done"
