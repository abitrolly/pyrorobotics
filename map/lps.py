import Tkinter
from math import cos, sin, pi, sqrt

class LPS(Tkinter.Tk):
   def __init__(self, cols, rows, value = 0.5,
                width = 200, height = 200,
                widthMM = 7000, heightMM = 7000):
      Tkinter.Tk.__init__(self)
      self.title("Local Perceptual Space")
      self.width = width
      self.height = height
      self.cols = cols
      self.rows = rows
      self.widthMM = widthMM
      self.heightMM = heightMM
      self.xScaleMM = self.widthMM / self.cols
      self.yScaleMM = self.heightMM / self.rows
      self.xScale = self.width / self.cols
      self.yScale = self.height / self.rows
      self.reset()
      self.step = 0
      self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height)
      self.bind("<Configure>", self.changeSize)
      self.canvas.bind("<B1-Motion>", self.increaseCell)
      self.canvas.bind("<B2-Motion>", self.middleCell)
      self.canvas.bind("<B3-Motion>", self.decreaseCell)
      self.canvas.bind("<Button-1>", self.increaseCell)
      self.canvas.bind("<Button-2>", self.middleCell)
      self.canvas.bind("<Button-3>", self.decreaseCell)
      self.canvas.bind("<KeyPress-q>", self.close)
      self.canvas.pack()
      self.protocol('WM_DELETE_WINDOW',self.close)
      self.update_idletasks()

   def reset(self, value = 0.5):
      self.grid = [[value for col in range(self.cols)]
                   for row in range(self.rows)]
      self.label = [['' for col in range(self.cols)]
                    for row in range(self.rows)]

   def increaseCell(self, event):
      y = event.x
      x = event.y
      self.grid[int(x / self.xScale)][int(y / self.yScale)] = 1.0
      self.redraw()

   def middleCell(self, event):
      y = event.x
      x = event.y
      self.grid[int(x / self.xScale)][int(y / self.yScale)] = 0.5
      self.redraw()

   def decreaseCell(self, event):
      y = event.x
      x = event.y
      self.grid[int(x / self.xScale)][int(y / self.yScale)] = 0.0
      self.redraw()

   def changeSize(self, event):
      self.width = self.winfo_width() - 2
      self.height = self.winfo_height() - 2
      self.canvas.configure(width = self.width, height = self.height)
      self.xScale = self.width / self.cols
      self.yScale = self.height / self.rows
      self.redraw()

   def color(self, value, maxvalue):
      value = 1.0 - value / maxvalue
      color = "gray%d" % int(value * 100.0) 
      return color

   def close(self, event = 0):
      self.withdraw()
      self.update_idletasks()

   def setArc(self, th, dist, offx = 0, offy = 0, label = '', arc = 0.5):
      originMM = self.widthMM / 2.0, self.heightMM / 2.0
      xhit = cos(th) * dist + offx
      yhit = sin(th) * dist - offy
      xpos = int((originMM[0] + xhit) / self.xScaleMM)
      ypos = int((originMM[1] - yhit) / self.yScaleMM)
      self.label[ypos][xpos] = label
      self.grid[ypos][xpos] = 1.0

   def plotSensor(self, robot, item):
      units = robot.get('sonar', 'units')
      robot.set('sonar', 'units', 'METERS')
      for i in range(robot.get(item, 'count')):
         offx, offy = robot.get(item, 'ox', i), robot.get(item, 'oy', i)
         dist = robot.get(item, 'value', i)
         angle = robot.get(item, 'th', i)
         if dist < robot.get(item, 'maxvalue'):
            self.setArc(angle, dist * 1000, offx = offx, offy = offy,
                        label = "%d" % i)
      robot.set('sonar', 'units', units)

   def redraw(self):
      maxval = 1
      for i in range(self.rows):
         for j in range(self.cols):
            self.canvas.create_rectangle(int(j * self.xScale),
                                         int(i * self.yScale),
                                         int((j + 1) * self.xScale),
                                         int((i + 1) * self.yScale),
                                         width = 0,
                                         fill=self.color(self.grid[i][j],
                                                         maxval),
                                         tag = "cell%d" % self.step)
            if self.label[i][j]:
               self.canvas.create_text(int((j + .5) * self.xScale),
                                       int((i + .5) * self.yScale),
                                       text = self.label[i][j],
                                       fill="yellow",
                                       tag = "cell%d" % self.step)
      self.canvas.create_oval( self.width / 2.0 - 10,
                               self.height / 2.0 - 10,
                               self.width / 2.0 + 10,
                               self.height / 2.0 + 10,
                               fill = "red",
                               tag = "cell%d" % self.step)
      self.canvas.create_rectangle( self.width / 2.0 + 5,
                               self.height / 2.0 - 5,
                               self.width / 2.0 + 15,
                               self.height / 2.0 + 5,
                               fill = "blue",
                               tag = "cell%d" % self.step)
                               
      self.step = not self.step
      self.canvas.delete("cell%d" % self.step)
      self.update_idletasks()

if __name__ == '__main__':
   lps = LPS(10, 10)
   lps.redraw()
   lps.mainloop()
