from Tkinter import *

class Slider:

   def __init__(self, variable = "x", value = 0, minVal = 0, maxVal = 100):
      self.app = Tk()
      self.app.withdraw()
      self.win = Toplevel()
      self.win.wm_title(variable)
      self.win.protocol('WM_DELETE_WINDOW',self.destroy)
      self.frame = Frame(self.win)
      self.variable = variable
      length = 100
      ticks = (maxVal - minVal) / 2
      self.scale = Scale(self.frame, orient=HORIZONTAL, length = length, \
                         from_=minVal, to=maxVal, tickinterval=ticks,\
                         command = self.getValue)
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
   slider = Slider("x", 50, 0, 255)
   slider.app.after(100,slider.update)
   slider.app.mainloop()
