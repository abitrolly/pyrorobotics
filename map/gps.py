from pyro.map.tkmap import TkMap
from math import cos, sin, pi, sqrt

class GPS(TkMap):
   """
   GUI for visualizing the global perceptual space of a robot.
   """
   def __init__(self, cols, rows, value = 0.5,
                width = 400, height = 400,
                widthMM = 10000, heightMM = 10000,
                title = "Global Perceptual Space"):
      """ Pass in grid cols, grid cells, and total width/height in MM"""
      self.step = 0
      TkMap.__init__(self, cols, rows, value,
                     width, height,
                     widthMM, heightMM, title)

   def redraw(self):
       pass

   def updateFromLPS(self, lps, robot):
       # things we will need:
       #grid, x, y, th, cellxMM, cellyMM:
       grid = lps.grid
       #self.canvas.delete("old")
       x = robot.getX() * 1000
       y = robot.getY() * 1000
       thr = robot.getThr()
       # going to plot each cell:
       #for row in range(len(grid)):
       #    for col in range(len(grid[row])):
       #        figure out which cell its in
       #        plot it
       #        self.grid[][] = grid[row][col]
       # for now, just plot robot:
       xpos = int(x / self.colScaleMM)
       # In GPS, the origin is at the bottom left corner.
       # This matches the way world files are specified.
       ypos = self.rows - int(y / self.rowScaleMM) - 1
       if self.inRange(ypos, xpos) and self.grid[ypos][xpos] != 1.0:
           self.grid[ypos][xpos] = 1.0
           self.plotCell(ypos, xpos, "red")
       for i in range(lps.rows):
          for j in range(lps.cols):
             if lps.grid[i][j] > .5:
                # y component is negative because y up is positive
                xMM = (j - (lps.cols / 2)) * lps.colScaleMM
                yMM = -1 * (i - (lps.rows / 2)) * lps.rowScaleMM
                # cos(0) = 1, sin(0) = 0
                xrot = (xMM * cos(thr) - yMM * sin(thr))
                yrot = (xMM * sin(thr) + yMM * cos(thr))
                xhit = x + xrot 
                yhit = y + yrot 
                xcell = int(xhit / self.colScaleMM)
                ycell = self.rows - int(yhit / self.rowScaleMM) - 1
                self.plotCell( ycell, xcell, "black")

   def plotCell(self, ypos, xpos, color):
      self.canvas.create_rectangle(int(xpos * self.colScale),
                                   int(ypos * self.rowScale),
                                   int((xpos + 1) * self.colScale),
                                   int((ypos + 1) * self.rowScale),
                                   width = 0,
                                   fill=color, tag = "old")


if __name__ == '__main__':
    gps = GPS(50, 50)
    gps.application = 1
    gps.mainloop()
