# -------------------------------------------------------
# Hinton Diagram
# -------------------------------------------------------

from OpenGL.Tk import *
import os

class Hinton: # Plot
   def __init__(self, blocks, title = None, width = 275, maxvalue = 1.0):
      self.win = Tk()
      self.maxvalue = maxvalue
      self.width = width
      self.height = abs(width / float(blocks))
      if title == None:
         self.win.wm_title("hinton@%s:"%os.getenv('HOSTNAME'))
      else:
         self.win.wm_title(title)
      self.canvas = Canvas(self.win,width=width,height=self.height)
      self.canvas.pack()
      self.even = 0
      self.update([1.0] * blocks)
        
   def setTitle(self, title):
      self.win.wm_title(title)
      
   def update(self, vector):
      if self.even:
         label = 'even'
         last = 'odd'
      else:
         label = 'odd'
         last = 'even'
      self.even = not self.even
      blocksize = abs(self.width / float(len(vector)))
      b = blocksize / 2.0
      y = b
      for v in range (len(vector)):
         x = blocksize * v + b
         size = abs(vector[v]/float(self.maxvalue)) * blocksize * .8 / 2.0 
         if vector[v] < 0.0:
            color = 'red'
         else:
            color = 'black'
         try:
            self.canvas.create_rectangle(x - size,
                                         y - size,
                                         x + size,
                                         y + size,
                                         width = 0,
                                         tag = label,
                                         fill = color)
         except:
            pass
      self.canvas.delete(last)

if __name__ == '__main__':
   hinton1 = Hinton(6)
   hinton1.update([0.0, 1.0, .5, 0.0, -1.0, -.5])
   hinton2 = Hinton(7)
   hinton2.update([1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0])
   hinton1.win.mainloop()
   hinton2.win.mainloop()
