import Tkinter
from math import cos, sin, pi, sqrt

class LPS(Tkinter.Tk):
   """
   GUI for visualizing the local perceptual space of a robot.
   """
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
      self.colScaleMM = self.widthMM / self.cols
      self.rowScaleMM = self.heightMM / self.rows
      self.colScale = self.width / self.cols
      self.rowScale = self.height / self.rows
      self.reset()
      self.step = 0
      self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height)
      self.bind("<Configure>", self.changeSize)
      self.canvas.pack()
      self.protocol('WM_DELETE_WINDOW', self.close)
      self.update_idletasks()

   def reset(self, value = 0.5):
      self.grid = [[value for col in range(self.cols)]
                   for row in range(self.rows)]
      self.label = [['' for col in range(self.cols)]
                    for row in range(self.rows)]

   def changeSize(self, event):
      self.width = self.winfo_width() - 2
      self.height = self.winfo_height() - 2
      self.canvas.configure(width = self.width, height = self.height)
      self.colScale = self.width / self.cols
      self.rowScale = self.height / self.rows
      self.redraw()

   def color(self, value, maxvalue):
      value = 1.0 - value / maxvalue
      color = "gray%d" % int(value * 100.0) 
      return color

   def close(self, event = 0):
      self.withdraw()
      self.update_idletasks()

   def plotSensor(self, robot, item):
      """
      Point (0,0) is located at the center of the robot.
      Point (offx, offy) is the location of the sensor on the robot.
      Theta is angle of the sensor hit relative to heading 0.
      Dist is the distance of the hit from the sensor.
      Given these values, need to calculate the location of the hit
      relative to the center of the robot (xhit, yhit).  

                    .(xhit, yhit)
                   /
                  / 
                 /  
           dist /   
               /    
              /     
             /theta 
            .-------
           (offx, offy)
        
      .-->heading 0
      (0,0)
      
      """
      originalUnits = robot.get(item, 'units')
      robot.set(item, 'units', 'METERS')
      for i in range(robot.get(item, 'count')):
         offx, offy = robot.get(item, 'ox', i), robot.get(item, 'oy', i)
         dist = robot.get(item, 'value', i) 
         theta = robot.get(item, 'th', i)
         if dist < robot.get(item, 'maxvalue'):
            # calculate point in LPS coordinates
            dist *= 1000
            xhit = cos(theta) * dist + offx
            yhit = sin(theta) * dist + offy
            # transform point to GUI coordinates
            originMM = self.widthMM / 2.0, self.heightMM / 2.0
            xpos = int((originMM[0] + xhit) / self.colScaleMM)
            ypos = int((originMM[1] - yhit) / self.rowScaleMM)
            self.label[ypos][xpos] = "%d" % i
            self.grid[ypos][xpos] = 1.0
      robot.set(item, 'units', originalUnits)

   def redraw(self):
      maxval = 1
      for i in range(self.rows):
         for j in range(self.cols):
            self.canvas.create_rectangle(int(j * self.colScale),
                                         int(i * self.rowScale),
                                         int((j + 1) * self.colScale),
                                         int((i + 1) * self.rowScale),
                                         width = 0,
                                         fill=self.color(self.grid[i][j],
                                                         maxval),
                                         tag = "cell%d" % self.step)
            if self.label[i][j]:
               self.canvas.create_text(int((j + .5) * self.colScale),
                                       int((i + .5) * self.rowScale),
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
