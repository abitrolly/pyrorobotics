from Tkinter import *

class Slider:

   def __init__(self, variable = "x", minVal = 0, maxVal = 100, value = None):
      self.app = Tk()
      self.app.withdraw()
      self.win = Toplevel()
      self.win.wm_title(variable)
      self.win.protocol('WM_DELETE_WINDOW',self.destroy)
      self.frame = Frame(self.win)
      self.variable = variable
      if value == None:
         value = (maxVal + minVal) / 2.0
      resolution = -1 # (maxVal - minVal) / 100.0
      ticks = (maxVal - minVal) / 4.0
      self.scale = Scale(self.frame, orient=HORIZONTAL, length = 300, \
                         from_=minVal, to=maxVal, tickinterval=ticks,\
                         command = self.getValue, resolution = resolution)
      self.scale.set(value)
      self.frame.pack(fill = "both")
      self.scale.pack(fill = "both")
      
   def getValue(self, event = None):
      return self.scale.get()

   def update(self):
      try:
         print self.variable, "=", self.getValue()
         self.app.after(100,self.update)
      except:
         pass

   def destroy(self):
      self.win.destroy()

if __name__ == '__main__':
   # just to test
   slider = Slider("x", 0.0, 10.0)
   slider.app.after(100,slider.update)
   slider.app.mainloop()
