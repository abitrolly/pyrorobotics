#A set of model vector visualization tools.
#Each visualizer should be a subclass of VisVector, which is an abstract class.
#If a visualizer is added, it should be added to the if statement in
#VisVectorFactory.  Each new class should follow the nameing convention
#XVisVector, where X is the string that gets passed to VisVectorFactory

from pyro.brain.psom import *
from Tkinter import *

class VisVector:
   """
   This is an abstract base class for a set of vector visualizers.
   Each subclass should be made specifically for a type of vector.
   """

   def __init__(self, vector, title=""):
      raise "This is an abstract function."

   def close(self):
      raise "This is an abstract function."

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
         ll.pack(side=LEFT)
         rl = Label(Rframe, text="= " + str(self.vector[i]))
         rl.pack(side=LEFT)

   def close(self):
      """Close the window"""
      self.win.destroy()

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
         ll.pack(side=LEFT)
         rl = Label(Rframe, text="= " + str(self.vector[i]))
         rl.pack(side=LEFT)

   def close(self):
      """Close the window"""
      self.win.destroy()

def VisVectorFactory(type, vector, title=""):
   """
   Given a type of VisVector as a string, create and initialize an
   instance of that type, and return a reference.
   """
   if type == "IR":
      return IRVisVector(vector, title)
   elif type == "Generic":
      return GenericVisVector(vector, title)
   else:
      raise "VisVector type not supported"
