# -------------------------------------------------------
# Hinton Diagram
# -------------------------------------------------------

from OpenGL.Tk import *
import os

class Hinton: # Plot
   def __init__(self, blocks = 1, title = None, width = 275, maxvalue = 1.0, data = None):
      """
      Arguments:

      blocks: the starting number of vectors to plot [1]
      title: the title of the Plot window [hinton@$HOSTNAME]
      width: the starting width of the plot window [275]
      maxvalue: The maximum magnitude of the plots [1.0]
      data: The vector to initialize the plot with [None]
      """
      self.win = Tk()
      self.maxvalue=maxvalue
      self.width=width
      if data:
         blocks = len(data)
      self.height = abs(width / float(blocks))
      if title == None:
         self.win.wm_title("hinton@%s:"%os.getenv('HOSTNAME'))
      else:
         self.win.wm_title(title)
      self.canvas = Canvas(self.win,width=width,height=self.height)
      self.canvas.bind("<Configure>", self.changeSize)
      self.canvas.pack(fill=BOTH)
      self.even = 0
      if data:
         self.update(data)
      else:
         self.update([1.0] * blocks)
        
   def setTitle(self, title):
      self.win.wm_title(title)

   def changeSize(self, event):
      self.width = self.canvas.winfo_width() - 2
      self.update(self.last)
      
   def update(self, vec):
      #make a copy of vec, so we can modify the values for bounds checking
      self.last = vec
      vector = vec[:]
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
         if vector[v] < 0.0:
            color = 'red'
         else:
            color = 'black'
         #if the vector is greater in magnitude than maxvalue, set it
         #to maxvalue and change the color to indicate that it's out
         #of bounds
         if vector[v] > self.maxvalue:
            vector[v] = self.maxvalue
            color = 'green'
         elif vector[v] < -self.maxvalue:
            vector[v] = -self.maxvalue
            color = 'blue'
         x = blocksize * v + b
         size = abs(vector[v]/float(self.maxvalue)) * blocksize * .8 / 2.0 
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
   v = [1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -5.0]
   hinton2.update(v)
   print v
   hinton1.win.mainloop()
   hinton2.win.mainloop()
