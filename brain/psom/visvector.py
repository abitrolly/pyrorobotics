#A set of model vector visualization tools.
#Each visualizer should be a subclass of VisVector, which is an abstract class.
#If a visualizer is added, it should be added to the if statement in
#VisVectorFactory.  Each new class should follow the nameing convention
#XVisVector, where X is the string that gets passed to VisVectorFactory

from pyro.brain.psom import *
from Tkinter import *
import struct
from PIL import ImageTk
import pyro.gui.plot.hinton

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

class HintonVisVector(VisVector, pyro.gui.plot.hinton.Hinton):
   """
   Use the Hinton plot to display the vector
   """
   def __init__(self, vector, maxval=None, title=""):
      if not maxval:
         maxval = max(vector)
      pyro.gui.plot.hinton.Hinton.__init__(self, data=vector.get_elts(),
                                           maxvalue=maxval, title=title)
      b = Button(self.win, text="Close", command=self.close)
      b.pack()

class BarGraphVisVector(VisVector):
   """
   Display a vector as a series of horizonal bars
   """
   def __init__(self, vector, minval=None, maxval=None, title=""):
      """
      Min and max can either be scalar minima and maxima for the
      entire vector, or it can be a list of the same length as the vector,
      each element corresponding to an element of the vector
      """
      self.vector = vector.get_elts()
      self.length = len(self.vector)

      #if the min and max are given as scalar values,
      #convert them to vectors of the length of the
      #vector
      
      try:
         len(minval)
         self.min = minval
      except TypeError:
         if minval == None:
            self.min = [min(self.vector)] * self.length
         else:
            self.min = [minval] * self.length

      try:
         len(maxval)
         self.max = maxval
      except TypeError:
         if max == None:
            self.max = [max(self.vector)] * self.length
         else:
            self.max = [maxval] * self.length

      self.win = Tk()
      self.win.title(title)
      for i in range(len(self.vector)):
         c = Canvas(self.win, height= 20, width = 100)
         c.create_text(2, 10, anchor=W, text=str(i))
         vec_len = abs(int((self.vector[i] / (self.max[i] - self.min[i])) * 85))
         c.create_rectangle(15, 3, vec_len + 15, 17, fill="red")
         c.pack()
         
      b = Button(self.win, text="Close", command=self.close)
      b.pack(side=BOTTOM)

      
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
   elif type == "BarGraph":
      return BarGraphVisVector
   elif type =="Hinton":
      return HintonVisVector
   else:
      raise "VisVector type not supported"

#  if __name__=="__main__":
#     from pyro.brain.psom import *
#     grayvis = getVisVectorByName("Grayscale")
#     piclist = [float(x)/255.0 for x in range(256)]
#     grayvis(vector(piclist), 16, 16)
#     print "Done"
