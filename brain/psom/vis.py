from pyro.brain.psom import *
from pyro.brain.psom.visvector import *
from Tkinter import *

ACT_MAX = 5
GRAY_STEP = 20

class VisPsom(psom):
   """
   A vizualized psom class.
   Takes all the same arguments as the psom class, with the following added
   keyword arguments:

   vis_radius:  The radius (in pixels) of the som cells.  Defaults to 15

   vis_padding: The amount of space (in pixels) on each side of each cell.
      Defaults to 2

   vis_vectortype:  The type of VisVector vizualier to use to display the
      model vectors.  Defaults to 'generic'.  See visvector.py.
   """

   def __init__(self, *args, **keys):
      self.last_x = 0
      self.last_y = 0
      #get Vis-specific keyword arguements out
      if 'vis_radius' in keys.keys():
         self.vis_radius = keys['vis_radius']
         del keys['vis_radius']
      else:
         self.vis_radius = 15
      if 'vis_padding' in keys.keys():
         self.vis_padding = keys['vis_padding']
         del keys['vis_padding']
      else:
         self.vis_padding = 2
      if 'vis_vectortype' in keys.keys():
         self.vectortype = keys['vis_vectortype']
         del keys['vis_vectortype']
      else:
         self.vectortype = "Generic"
      if 'title' in keys.keys():
         title = keys['title']
         del keys['title']
      else:
         title = "VisPsom"
      if 'opts' in keys.keys():
         self.opts = keys['opts']
         del keys['opts']
      else:
         self.opts = None

        
      psom.__init__(self, *args, **keys)

      self.win = Tk()
      self.win.wm_title(title)

      cellwidth = (self.vis_padding + self.vis_radius) * 2
      #offset to set off the rows for a hexagonal topology
      if self.topol == 'hexa':
         offset = cellwidth/2
      else: #topol = 'rect'
         offset = 0
      self.canvas = Canvas(self.win,
                           width=self.xdim * (2*self.vis_radius+2*self.vis_padding) + offset,
                           height=self.ydim * (2*self.vis_radius+2*self.vis_padding),
                           bg='white')
      self.canvas.bind("<ButtonRelease-1>", self.canvas_clicked_up)
      self.canvas.bind("<Button-1>", self.canvas_clicked_down)
      self.canvas.pack(side=TOP)
      f = Frame(self.win)
      self.showCount = "Train"
      self.toggleCount = Button(f, text="Show Map Count",
                                command=self.countSwitch)
      self.toggleCount.pack()
      f.pack(side=BOTTOM)

      self.lastMapped = (0,0)
      self.cells = []
      self.cellhash = {}
      self.history = {}

      for y in range(self.ydim):
         self.cells.append([])
         for x in range(self.xdim):
            x0 = (cellwidth * x) + self.vis_padding + (offset * (y % 2))
            y0 = (cellwidth * y) + self.vis_padding
            x1 = x0 + (self.vis_radius * 2)
            y1 = y0 + (self.vis_radius * 2)
            cell = self.canvas.create_oval(x0, y0, x1, y1, fill='white',
                                           tags = 'cell')
            center = ((x0 + x1)/2, (y0 + y1)/2)
            traintext = self.canvas.create_text(center[0], center[1],
                                                text = "",
                                                fill = 'blue',
                                                tags = 'traincount')
            maptext = self.canvas.create_text(center[0], center[1],
                                              text = "",
                                              fill = 'red',
                                              tags = 'mapcount')
            self.cells[y].append({"cell" : cell,"traincount" : 0,"mapcount": 0,
                                  "traintext" : traintext, "maptext": maptext})
            self.cellhash[cell] = (x, y)

      self.canvas.tag_lower('cell', 'traincount')
      self.canvas.tag_lower('mapcount', 'cell')
            
#      self.win.mainloop()

   def canvas_clicked_up(self, event):
      celllist = self.canvas.find_overlapping(event.x, event.y,
                                              event.x, event.y)
      cell = None
      for item in celllist:
         if item in self.cellhash.keys():
            cell = item
            break
                                          
      if cell:
         x, y = self.cellhash[cell]
         vec = self.get_model_vector(point(x, y))
         if x == self.last_x and y == self.last_y:
            visclass = getVisVectorByName(self.vectortype)
            if self.opts: # override defaults
               visclass(vec, title="(%d, %d)" % (x, y), opts = self.opts)
            else:
               visclass(vec, title="(%d, %d)" % (x, y))
         else:
            # show difference
            vec2 = self.get_model_vector(point(self.last_x, self.last_y))
            diffvec = []
            for v in range(len(vec2)):
               diffvec.append( vec[v] - vec2[v] )
            myvector = vector( diffvec )
            visclass = getVisVectorByName(self.vectortype)
            if self.opts:
               visclass(myvector, title="(%d, %d) diff (%d, %d)"
                        % (x, y, self.last_x, self.last_y), opts = self.opts)
            else:
               visclass(myvector, title="(%d, %d) diff (%d, %d)"
                        % (x, y, self.last_x, self.last_y))

   def canvas_clicked_down(self, event):
      celllist = self.canvas.find_overlapping(event.x, event.y,
                                              event.x, event.y)
      cell = None
      for item in celllist:
         if item in self.cellhash.keys():
            cell = item
            break

      if cell:
         self.last_x, self.last_y = self.cellhash[cell]

   def countSwitch(self):
      if self.showCount == "Map":
         self.canvas.tag_raise('traincount', 'cell')
         self.canvas.tag_lower('mapcount', 'cell')
         self.toggleCount.configure(text="Show Map Count")
         self.showCount = "Train"
      elif self.showCount == "Train":
         self.canvas.tag_raise('mapcount', 'cell')
         self.canvas.tag_lower('traincount', 'cell')
         self.toggleCount.configure(text="Show Train Count")
         self.showCount = "Map"
         
   def inccount(self, x, y, which):
      """
      Update the hit count of a cell, and change the label.
      """
      self.cells[y][x][which+"count"] += 1
      self.canvas.itemconfigure(self.cells[y][x][which+"text"],
                                text = str(self.cells[y][x][which+"count"]))

   def _setcell(self, x, y, level):
      try:
         self.canvas.itemconfigure(self.cells[y][x]["cell"],
                                   fill='gray' + str(level))
      except:
         pass

   def _updatefill(self):
      for pt in self.history.keys():
         act = self.history[pt]
         self._setcell(pt[0], pt[1], (ACT_MAX - act) * GRAY_STEP)
         #decrease activation by 1
         if act == 0:
            del self.history[pt]
         else:
            self.history[pt] -= 1
            
   def clearfill(self):
      """
      Clears the markers, the count printout, and resets the count to 0
      for all cells.
      """
      for y in range(self.ydim):
         for x in range(self.xdim):
            self._setcell(x, y, 100)
            self.cells[x][y]['count'] = 0
      self.canvas.delete('count')

   def map(self, vector):
      retval = psom.map(self,vector)
      pt = retval.point.x, retval.point.y
      self._setcell(self.lastMapped[0], self.lastMapped[1], 100)
      self.canvas.itemconfigure(self.cells[pt[1]][pt[0]]["cell"],
                                fill = 'green')
      self.lastMapped = pt
      self.inccount(pt[0], pt[1], 'map')
      return retval

   def train(self, vector):
      retval = psom.train(self,vector)
      pt = retval.point.x, retval.point.y
      self.history[pt] = ACT_MAX
      self.inccount(pt[0], pt[1], 'train')
      self._updatefill()
      return retval

if __name__ == "__main__":
   mysom = VisPsom(file='ex.cod', vis_vectortype="Hinton")
   mydataset = dataset(file='ex.dat')
   mysom.init_training(0.02,4.0,5000)
   mysom.train_from_dataset(mydataset)
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()
   mysom.map(vector([14.0, 10.0, .3, -.8, 400.0]))
   raw_input()
   mysom.map(vector([10.0, 30.0, -.3, .8, 375.0]))
   raw_input()
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()         
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()            
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()                        
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   raw_input()
