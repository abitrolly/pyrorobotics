import math, string
from Tkinter import *
from pyro.robot.saphira import *
import sys
import gridio
import pyro.gui.console as console

from spg import *
class GridTest:
   def reset(self):
      self.robo.act('localize', 0, 0, 0)
      for y in range(0, self.gridsize):
         for x in range(0, self.gridsize):
            if self.cell_list[x][y]:
               self.c.delete(self.cell_list[x][y])
               self.cell_list[x][y] = 0
      
   def __init__(self, global_size, local_size):
      self.scale = 6.0
      self.robo = SaphiraRobot()

      #self.cellsize = 1
      
      ###self.gridsize = size # size * size cells
      self.gridsize = global_size # size * size cells
      self.local_grid_size = local_size
      self.gi = gridio.gridinterface(self.robo, \
                                     self.gridsize, self.local_grid_size)
      # GLOBAL grid
      self.root = Tk()
      self.c = Canvas(self.root)
      self.c.configure(width = self.gridsize * self.scale)
      self.c.configure(height = self.gridsize * self.scale)
      self.c.configure(background="black")
      self.c.pack()
      self.cell_list = []
      for y in range(0, self.gridsize):
         self.cell_list.append([])
         for x in range(0, self.gridsize):
            self.cell_list[y].append(0)


      # LOCAL grid
      self.lgrid_root = Tk()
      self.lgrid_c = Canvas(self.lgrid_root)
      self.lgrid_c.configure(width = self.local_grid_size * self.scale)
      self.lgrid_c.configure(height = self.local_grid_size * self.scale)
      self.lgrid_c.configure(background="black")
      self.lgrid_c.pack()
      self.lgrid_cell_list = []
      for y in range(0, self.local_grid_size):
         self.lgrid_cell_list.append([])
         for x in range(0, self.local_grid_size):
            self.lgrid_cell_list[y].append(0)

      while(1):
         self.update()
         
   def update(self):
      self.robo.update()
      SpacePerceptionGrid_reset(self.gi.local_grid)
      updated_region = self.gi.updategrid()
      if updated_region: # local grid was recentered
         y0 = updated_region[0]
         x0 = updated_region[1]
         w  = updated_region[2]
         h  = updated_region[3]
         print (w, h)
         self.draw(1, x0, y0, w, h)
      
      self.draw(0, 0, 0, self.local_grid_size, self.local_grid_size)

      
      self.prompt()
      
      self.lgrid_c.update()
      self.lgrid_c.after(1000)
      
      self.robo.act('move', 0, 0)
      
      self.c.update()
      self.c.after(50)

      robo = self.robo
      print "robot: ", robo.get('robot', 'x'), robo.get('robot', 'y')
      
   def prompt(self):
      r = self.robo

      r.act('move', 0, 0)

      dir = raw_input("l, r, f, b, q, x, or [return]> ")
      if dir == 'l':
         r.act('rotate', 0.5)
      elif dir == 'r':
         r.act('rotate', -0.5)
      elif dir == 'f':
         r.act('translate', 0.5)
      elif dir == 'b':
         r.act('translate', -0.5)
      elif dir == 'q':
         r.Disconnect()
         sys.exit(1)
      elif dir == 'x':
         self.gi.reset()
         self.reset()
      else:
         pass


   def draw(self, is_global, x0, y0, w, h):
      if is_global == 1:
         gridsize = self.gridsize
         canvas = self.c
         cell_list = self.cell_list
         getoccupancy = self.gi.getoccupancy
      elif is_global == 0:
         gridsize = self.local_grid_size
         canvas = self.lgrid_c
         cell_list = self.lgrid_cell_list
         getoccupancy = self.gi.getlocaloccupancy
      else:
         return

      #if is_global:
      #   print "going to draw %d to %d, %d to %d", \
      #         (x0, x0 + gridsize, y0, y0 + gridsize)
      for x in range(x0, x0 + w): 
         for y in range(y0 , y0 + h): 
            occupancy = getoccupancy(x, y)

            if occupancy == 0: # it's nothing
               rgb = "#000000"
            elif occupancy > 0: # it's clear!
               intensity = min(occupancy, 30) / 30.0 * 50.0 + 49.0
               r = g = b  = ("00%d" % intensity)[-2:]
               rgb = "#%s%s%s" % (r, g, b)
            else: # it's a hit
               intensity = min(abs(occupancy), 30) / 30.0 * 50.0 + 49.0
               b = "00"
               r = g = ("00%d" % intensity)[-2:]
               rgb = "#%s%s%s" % (r, g, b)
            if (x - x0 == self.local_grid_size / 2) and \
               (y - y0 == self.local_grid_size / 2) and is_global:
               rgb = "#FF0000"
                  
            if cell_list[x][y]:
               canvas.itemconfigure(cell_list[x][y], \
                                    outline=rgb, fill=rgb)
            else:
               cell_list[x][y] = canvas.create_oval(
                  x * self.scale - self.scale/2.0,\
                  y * self.scale - self.scale/2.0,\
                  x * self.scale + self.scale/2.0,\
                  y * self.scale + self.scale/2.0,\
                  fill=rgb,\
                  outline=rgb)
     
if (__name__ == '__main__'):
   gt = GridTest(100, 30) # global grid size, local grid size
   # when plotting 100/2 = 50 should be added to
   # center the points

      
