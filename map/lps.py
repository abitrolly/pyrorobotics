import Tkinter
from math import cos, sin, pi, sqrt

class LPS(Tkinter.Tk):
   """
   GUI for visualizing the local perceptual space of a robot.
   """
   def __init__(self, cols, rows, value = 0.5,
                width = 200, height = 200,
                widthMM = 7500, heightMM = 7500):
      """ Pass in grid cols, grid cells, and total width/height in MM"""
      Tkinter.Tk.__init__(self)
      self.debug = 0
      self.title("Local Perceptual Space")
      self.width = width
      self.height = height
      self.cols = cols
      self.rows = rows
      self.widthMM = widthMM
      self.heightMM = heightMM
      self.originMM = self.widthMM / 2.0, self.heightMM / 2.0
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

   def destroy(self):
      self.withdraw()

   def reset(self, value = 0.5):
      self.grid = [[value for col in range(self.cols)]
                   for row in range(self.rows)]
      self.label = [['' for col in range(self.cols)]
                    for row in range(self.rows)]

   def changeSize(self, event):
      self.width = self.winfo_width() - 2
      self.height = self.winfo_height() - 2
      self.canvas.configure(width = self.width, height = self.height)
      # reset these, in case the MM's changed:
      self.originMM = self.widthMM / 2.0, self.heightMM / 2.0
      self.colScaleMM = self.widthMM / self.cols
      self.rowScaleMM = self.heightMM / self.rows
      # ----------------------------------
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

   def inRange(self, r, c):
      return r >= 0 and r < self.rows and c >= 0 and c < self.cols

   def setGridLocation(self, x, y, value, label = None):
      xpos = int((self.originMM[0] + x) / self.colScaleMM)
      ypos = int((self.originMM[1] - y) / self.rowScaleMM)
      if self.inRange(ypos, xpos):
         self.grid[ypos][xpos] = value
         if label != None:
            self.label[ypos][xpos] = "%d" % label

   def computeOccupancy(self, origx, origy, hitx, hity, arc, senseObstacle, label = None):
      """
      Initially only compute occupancies on the line from the robot to
      the sensor hit.  
      """
      if self.debug: print "occupancyGrid:", (origx, origy, hitx, hity)
      # set the origin of sensor empty:
      self.setGridLocation(origx, origy, 0.0)
      rise = hity - origy
      if abs(rise) < 0.1:
         rise = 0
      run  = hitx - origx
      if abs(run) < 0.1:
         run = 0
      steps = round(max(abs(rise/self.rowScaleMM), abs(run/self.colScaleMM)))
      if steps == 0:
         self.setGridLocation(hitx, hity, 1.0, label)
         return
      stepx = run / float(steps)
      if abs(stepx) > self.colScaleMM:
         stepx = self.colScaleMM
         if run < 0:
            stepx *= -1
      stepy = rise / float(steps)
      if abs(stepy) > self.rowScaleMM:
         stepy = self.rowScaleMM
         if rise < 0:
            stepy *= -1
      currx = origx
      curry = origy
      for step in range(steps):
         curry += stepy
         currx += stepx
         self.setGridLocation(currx, curry, 0.0, label)
      if senseObstacle:
         self.setGridLocation(hitx, hity, 1.0, label)
      else:
         self.setGridLocation(hitx, hity, 0.0, label)

   def sensorHits(self, robot, item):
      """
      Point (0,0) is located at the center of the robot.
      Point (offx, offy) is the location of the sensor on the robot.
      Theta is angle of the sensor hit relative to heading 0.
      Dist is the distance of the hit from the sensor.
      Given these values, need to calculate the location of the hit
      relative to the center of the robot (hitx, hity).  

                    .(hitx, hity)
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
      arc = robot.get(item, 'arc', 0)
      # FIX: fill in radius of robot:
      radius = robot.get('robot', 'radius')
      # -----------------------------------
      for i in range(robot.get(item, 'count')):
         # in MM:
         offx, offy = robot.get(item, 'ox', i), robot.get(item, 'oy', i)
         # in METERS, because we set it so above:
         dist = robot.get(item, 'value', i) 
         if dist < robot.get(item, 'maxvalue'):
            senseObstacle = 1
         else:
            senseObstacle = 0
         theta = robot.get(item, 'th', i) # in radians
         # convert to MMs:
         hitx = cos(theta) * dist * 1000 + offx
         hity = sin(theta) * dist * 1000 + offy
         self.computeOccupancy(offx, offy, hitx, hity, arc, senseObstacle, i)
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
