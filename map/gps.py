from pyro.map.tkmap import TkMap
from math import cos, sin, pi, sqrt

class GPS(TkMap):
   """
   GUI for visualizing the global perceptual space of a robot.
   """
   def __init__(self, cols, rows, value = 0.5,
                width = 400, height = 400,
                widthMM = 50000, heightMM = 50000,
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
       x = robot.getX() * 1000
       y = robot.getY() * 1000
       # going to plot each cell:
       #for row in range(len(grid)):
       #    for col in range(len(grid[row])):
       #        figure out which cell its in
       #        plot it
       #        self.grid[][] = grid[row][col]
       # for now, just plot robot:
       print "robot:", (x, y)
       xpos = int((self.originMM[0] + x) / self.colScaleMM)
       ypos = int((self.originMM[1] - y) / self.rowScaleMM)
       print "grid:", (xpos, ypos)
       if self.inRange(ypos, xpos) and self.grid[ypos][xpos] != 1.0:
           self.grid[ypos][xpos] = 1.0
           self.canvas.create_rectangle(int(xpos * self.colScale),
                                        int(ypos * self.rowScale),
                                        int((xpos + 1) * self.colScale),
                                        int((ypos + 1) * self.rowScale),
                                        width = 0,
                                        fill="red")


if __name__ == '__main__':
    gps = GPS(100, 100)
    gps.application = 1
    gps.mainloop()
