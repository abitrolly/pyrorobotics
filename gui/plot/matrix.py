# -------------------------------------------------------
# Matrix Plot (Images)
# -------------------------------------------------------

from OpenGL.Tk import *
import os

class Matrix: # Plot
   def __init__(self, cols = 1, rows = 1, title = None, width = 275, height = 275, maxvalue = 255.0, data = None):
      """
      Arguments:

      """
      self.win = Tk()
      self.maxvalue=maxvalue
      self.width=width
      self.height = height
      self.cols = cols
      self.rows = rows
      if title == None:
         self.win.wm_title("matrix@%s:"%os.getenv('HOSTNAME'))
      else:
         self.win.wm_title(title)
      self.canvas = Canvas(self.win,width=width,height=height)
      self.canvas.bind("<Configure>", self.changeSize)
      self.canvas.pack(fill=BOTH)
      self.even = 0
      if data:
         self.update(data)
      else:
         self.update([1.0] * cols * rows)
        
   def setTitle(self, title):
      self.win.wm_title(title)

   def changeSize(self, event):
      self.width = self.canvas.winfo_width() - 2
      self.update(self.last)
      
   def update(self, vec):
      self.last = vec[:]
      if self.even:
         label = 'even'
         last = 'odd'
      else:
         label = 'odd'
         last = 'even'
      self.even = not self.even
      x_blocksize = int(self.width / float(self.cols))
      y_blocksize = int(self.height / float(self.rows))
      x_b = x_blocksize / 2.0
      y_b = y_blocksize / 2.0
      for r in range (self.rows):
         for c in range (self.cols):
            v = r * self.cols + c
            color = "gray%d" % int((vec[v] / self.maxvalue) * 100.0) 
            x = x_blocksize * c + x_b
            y = y_blocksize * r + y_b
            try:
               self.canvas.create_rectangle(x - x_b,
                                            y - y_b,
                                            x + x_b,
                                            y + y_b,
                                            width = 0,
                                            tag = label,
                                            fill = color)
            except:
               pass
      try:
         self.canvas.delete(last)
      except:
         pass

if __name__ == '__main__':
   matrix1 = Matrix(3, 2)
   matrix1.update([0.0, 1.0, .5, 0.0, -1.0, -.5])
   matrix2 = Matrix(4, 2)
   v = [1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -5.0, 5.0]
   matrix2.update(v)
   print v
   matrix1.win.mainloop()
   matrix2.win.mainloop()