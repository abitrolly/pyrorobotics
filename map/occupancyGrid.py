import Tkinter

class occupancyGrid(Tkinter.Tk):
   """
   GUI for visualizing an occupancy grid style map.
   
   The mouse can be used to change occupancy values:
   Press the left button for 1.0
   Press the middle button for 0.5
   Press the right button  for 0.0

   Certain keys provide other funtionality:
   Press 'S' to set the start cell of the path.
   Press 'G' to set the goal cell of the path.
   Press 'P' to plan the path.
   Press '2' to double the size of the occupancy grid.
   Press 'Q' to quit.
   """
   def __init__(self, grid):
      Tkinter.Tk.__init__(self)
      self.title("Occupancy Grid")
      self.threshhold = 0.8
      self.grid = grid
      self.lastMatrix = self.grid
      self.lastPath = None
      self.colScale = 50.0
      self.rowScale = 50.0
      self.start = (0, 0)
      self.goal = (6, 2)
      self.rows = len(grid)
      self.cols = len(grid[0])
      self.width = self.cols * self.colScale
      self.height = self.rows * self.rowScale
      self.infinity = 1e5000
      self.value= [[self.infinity for col in range(self.cols)]
                   for row in range(self.rows)]
      self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height)
      self.bind("<Configure>", self.changeSize)
      self.canvas.bind("<B1-Motion>", self.increaseCell)
      self.canvas.bind("<B2-Motion>", self.middleCell)
      self.canvas.bind("<B3-Motion>", self.decreaseCell)
      self.canvas.bind("<Button-1>", self.increaseCell)
      self.canvas.bind("<Button-2>", self.middleCell)
      self.canvas.bind("<Button-3>", self.decreaseCell)
      self.canvas.bind("<KeyPress-p>", self.findPath)
      self.canvas.bind("<KeyPress-s>", self.setStart)
      self.canvas.bind("<KeyPress-g>", self.setGoal)
      self.canvas.bind("<KeyPress-2>", self.setDouble)
      self.canvas.bind("<KeyPress-q>", self.close)
      self.canvas.pack()
      self.protocol('WM_DELETE_WINDOW', self.close)
      self.update_idletasks()

   def increaseCell(self, event):
      cellCol = int(round(event.x/self.colScale))
      cellRow = int(round(event.y/self.rowScale))
      self.grid[cellRow][cellCol] = 1.0
      self.redraw( self.grid, None)

   def middleCell(self, event):
      cellCol = int(round(event.x/self.colScale))
      cellRow = int(round(event.y/self.rowScale))
      self.grid[cellRow][cellCol] = 0.5
      self.redraw( self.grid, None)

   def decreaseCell(self, event):
      cellCol = int(round(event.x/self.colScale))
      cellRow = int(round(event.y/self.rowScale))
      self.grid[cellRow][cellCol] = 0.0
      self.redraw( self.grid, None)

   def changeSize(self, event):
      self.width = self.winfo_width() - 2
      self.height = self.winfo_height() - 2
      self.canvas.configure(width = self.width, height = self.height)
      self.colScale = int(round(self.width / self.cols))
      self.rowScale = int(round(self.height / self.rows))
      self.redraw( self.lastMatrix, self.lastPath)

   def color(self, value, maxvalue):
      if value == self.infinity:
         return "brown"
      value = 1.0 - value / maxvalue
      color = "gray%d" % int(value * 100.0) 
      return color

   def close(self, event = 0):
      self.withdraw()
      self.update_idletasks()
      self.destroy()

   def setDouble(self, event):
      self.rows *= 2
      self.rowScale = int(round(self.height / self.rows))
      self.cols *= 2
      self.colScale = int(round(self.width / self.cols))
      self.value= [[self.infinity for col in range(self.cols)]
                   for row in range(self.rows)]
      self.grid= [[0.0 for col in range(self.cols)]
                  for row in range(self.rows)]
      self.redraw(self.grid)

   def setGoal(self, event):
      self.goal = int(round(event.x/self.colScale)), int(round(event.y/self.rowScale))
      self.redraw(self.grid)

   def setStart(self, event):
      self.start = int(round(event.x/self.colScale)), int(round(event.y/self.rowScale))
      self.redraw(self.grid)

   def findPath(self, event):
      path = self.planPath(self.start, self.goal, 50)
      if path:
         self.redraw(g.value, path)

   def redraw(self, matrix, path = None):
      self.lastMatrix = matrix
      self.lastPath = path
      maxval = 0.0
      for i in range(self.rows):
         for j in range(self.cols):
            if matrix[i][j] != self.infinity:
               maxval = max(matrix[i][j], maxval)
      if maxval == 0: maxval = 1
      self.canvas.delete("cell")
      for i in range(self.rows):
         for j in range(self.cols):
            self.canvas.create_rectangle(j * self.colScale,
                                         i * self.rowScale,
                                         (j + 1) * self.colScale,
                                         (i + 1) * self.rowScale,
                                         width = 0,
                                         fill=self.color(matrix[i][j], maxval),
                                         tag = "cell")
            if path and path[i][j] == 1:
               self.canvas.create_oval(j * self.colScale,
                                       i * self.rowScale,
                                       (j + .25) * self.colScale,
                                       (i + .25) * self.rowScale,
                                       width = 0,
                                       fill = "blue",
                                       tag = "cell")

      self.canvas.create_text((self.start[0] + .5) * self.colScale,
                              (self.start[1] + .5) * self.rowScale,
                              tag = 'cell',
                              text="Start", fill='green')
      self.canvas.create_text((self.goal[0] + .5) * self.colScale,
                              (self.goal[1] + .5) * self.rowScale,
                              tag = 'cell',
                              text="Goal", fill='green')

   def printMatrix(self, m):
      for i in range(self.rows):
         for j in range(self.cols):
            print "%8.2f" % m[i][j],
         print
      print "-------------------------------------------------"

   def planPath(self, start, goal, iterations):
      """
      Path planning algorithm is based on one given by Thrun in the
      chapter 'Map learning and high-speed navigation in Rhino' from
      the book 'Artificial Intelligence and Mobile Robots' edited by
      Kortenkamp, Bonasso, and Murphy.

      Made two key changes to the algorithm given.
      1. When an occupancy probability is above some threshold, assume
         that the cell is occupied and set its value for search to
         infinity.
      2. When iterating over all cells to update the search values, add
         in the distance from the current cell to its neighbor.  Cels
         which are horizontal or vertical from the current cell are
         considered to be a distance of 1, while cells which are diagonal
         from the current cell are considered to be a distance of 1.41.
      """
      startCol, startRow = start
      goalCol, goalRow = goal
      self.value= [[self.infinity for col in range(self.cols)] for row in range(self.rows)]
      if not self.inRange(goalRow, goalCol):
         raise "goalOutOfMapRange"
      self.value[goalRow][goalCol] = 0.0
      for iter in range(iterations):
         for row in range(self.rows):
            for col in range(self.cols):
               for i in [-1,0,1]:
                  for j in [-1,0,1]:
                     if self.inRange(row+i, col+j):
                        if self.grid[row][col] > self.threshhold:
                           self.value[row][col] = self.infinity
                        else:
                           if abs(i) == 1 and abs(j) == 1:
                              d = 1.41
                           else:
                              d = 1
                           adj = self.value[row+i][col+j] + self.grid[row+i][col+j] + d
                           self.value[row][col] = min(self.value[row][col], adj)
      return self.getPath(startRow, startCol)

   def getPath(self, startRow, startCol):
      path = [[0 for col in range(self.cols)] for row in range(self.rows)]
      row = startRow
      col = startCol
      steps = 0
      while not (self.value[row][col] == 0.0):
         path[row][col] = 1
         min = self.infinity
         nextRow = -1
         nextCol = -1
         for i in [-1,0,1]:
            for j in [-1,0,1]:
               if not (i == 0 and j == 0) and self.inRange(row+i, col+j):
                  if self.value[row+i][col+j] < min:
                     min = self.value[row+i][col+j]
                     nextRow = row+i
                     nextCol = col+j
         if nextRow == -1:
            print "No such path!"
            self.redraw(self.value)
            return None
         steps += 1
         row = nextRow
         col = nextCol
      path[row][col] = 1
      print "Path is %d steps" % steps
      return path

   def inRange(self, r, c):
      return r >= 0 and r < self.rows and c >= 0 and c < self.cols

if __name__ == '__main__':
   # An occupancy grid of a simple world with an L-shaped obstacle
   map = [[0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
          [0.5, 0.5, 0.5, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5],
          [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5],
          [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5],
          [0.5, 0.5, 0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5],
          [0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5],
          ]
   g = occupancyGrid(map)
   # Find a path from position 0,0 to a point on the other side of
   # the L-shaped obstacle.
   g.redraw(map)
   g.canvas.focus_set()
   g.mainloop()
