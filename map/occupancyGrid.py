import Tkinter

class occupancyGrid(Tkinter.Tk):
   def __init__(self, grid):
      Tkinter.Tk.__init__(self)
      self.title("Occupancy Grid")
      self.threshhold = 0.8
      self.grid = grid
      self.lastMatrix = self.grid
      self.lastPath = None
      self.xScale = 50.0
      self.yScale = 50.0
      self.start = (0, 0)
      self.goal = (6, 2)
      self.rows = len(grid)
      self.cols = len(grid[0])
      self.width = self.cols * self.xScale
      self.height = self.rows * self.yScale
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
      self.infinity = 1e5000
      self.value= [[self.infinity for col in range(self.cols)]
                   for row in range(self.rows)]
      self.protocol('WM_DELETE_WINDOW',self.close)
      self.update_idletasks()

   def increaseCell(self, event):
      y = event.x
      x = event.y
      self.grid[int(round(x / self.xScale))][int(round(y / self.yScale))] = 1.0
      self.redraw( self.grid, None)

   def middleCell(self, event):
      y = event.x
      x = event.y
      self.grid[int(round(x / self.xScale))][int(round(y / self.yScale))] = 0.5
      self.redraw( self.grid, None)

   def decreaseCell(self, event):
      y = event.x
      x = event.y
      self.grid[int(round(x / self.xScale))][int(round(y / self.yScale))] = 0.0
      self.redraw( self.grid, None)

   def changeSize(self, event):
      self.width = self.winfo_width() - 2
      self.height = self.winfo_height() - 2
      self.canvas.configure(width = self.width, height = self.height)
      self.xScale = int(round(self.width / self.cols))
      self.yScale = int(round(self.height / self.rows))
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
      self.yScale = int(round(self.height / self.rows))
      self.cols *= 2
      self.xScale = int(round(self.width / self.cols))
      self.value= [[self.infinity for col in range(self.cols)]
                   for row in range(self.rows)]
      self.grid= [[0.0 for col in range(self.cols)]
                  for row in range(self.rows)]
      self.redraw(self.grid)

   def setGoal(self, event):
      self.goal = int(round(event.x/self.xScale)), int(round(event.y/self.yScale))
      self.redraw(self.grid)

   def setStart(self, event):
      self.start = int(round(event.x/self.xScale)), int(round(event.y/self.yScale))
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
            self.canvas.create_rectangle(j * self.xScale,
                                         i * self.yScale,
                                         (j + 1) * self.xScale,
                                         (i + 1) * self.yScale,
                                         width = 0,
                                         fill=self.color(matrix[i][j], maxval),
                                         tag = "cell")
            if path and path[i][j] == 1:
               self.canvas.create_oval(j * self.xScale,
                                       i * self.yScale,
                                       (j + .25) * self.xScale,
                                       (i + .25) * self.yScale,
                                       width = 0,
                                       fill = "blue",
                                       tag = "cell")

      self.canvas.create_text((self.start[0] + .5) * self.xScale,
                              (self.start[1] + .5) * self.yScale,
                              tag = 'cell',
                              text="Start", fill='green')
      self.canvas.create_text((self.goal[0] + .5) * self.xScale,
                              (self.goal[1] + .5) * self.yScale,
                              tag = 'cell',
                              text="Goal", fill='green')

   def printMatrix(self, m):
      for i in range(self.rows):
         for j in range(self.cols):
            print "%8.2f" % m[i][j],
         print
      print "-------------------------------------------------"

      # Made several changes to algorithm given by Thrun in the chapter
      # "Map learning and high-speed navigation in Rhino" from the book
      # "Artificial Intelligence and Mobile Robots" edited by Kortenkamp,
      # Bonasso, and Murphy.
      
      # 1. When an occupancy probability is above some threshold, assume
      # that the cell is occupied and set its value for search to
      # infinity.
      
      # 2. When iterating over all cells to update the search values, add
      # in the distance from the current cell to its neighbor.

   def planPath(self, start, goal, iterations):
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
      #self.printMatrix(self.value)
      return self.getPath(startRow, startCol)

   def getPath(self, startRow, startCol):
      path = [[0 for col in range(self.cols)] for row in range(self.rows)]
      row = startRow
      col = startCol
      nextRow = -1
      nextCol = -1
      steps = 0
      while not (self.value[row][col] == 0.0):
         path[row][col] = 1
         min = self.infinity
         for i in [-1,0,1]:
            for j in [-1,0,1]:
               if not (i == 0 and j == 0) and self.inRange(row+i, col+j):
                  if self.value[row+i][col+j] < min:
                     min = self.value[row+i][col+j]
                     nextRow = row+i
                     nextCol = col+j
                     steps += 1
         if nextRow == -1:
            print "No such path!"
            self.redraw(self.value)
            return None
         row = nextRow
         col = nextCol
      path[row][col] = 1
      #self.printMatrix(path)
      print "Path is %d steps" % steps
      return path

   def inRange(self, r, c):
      return r >= 0 and r < self.rows and c >= 0 and c < self.cols

if __name__ == '__main__':
   # An occupancy grid of a simple world with an L-shaped obstacle
   map = [[0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
          [0.5, 0.5, 0.5, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5],
          [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5],
          [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.5, 1.5, 0.5],
          [0.5, 0.5, 0.5, 0.0, 0.5, 0.7, 0.5, 0.0, 1.0, 0.0],
          [0.0, 0.0, 0.0, 0.0, 0.5, 1.5, 0.5, 0.0, 1.0, 0.0],
          ]
   g = occupancyGrid(map)
   # Find a path from position 0,0 to a point on the other side of
   # the L-shaped obstacle.
   g.redraw(map)
   g.canvas.focus_set()
   g.mainloop()
   #raw_input("Press ENTER to Plan Path\n")
   #raw_input("Press ENTER when done\n")
