import math, string
from Tkinter import *
from pyro.robot.saphira import *
import sys
import gridio
import pyro.gui.console as console

class GridTest:
   def reset(self):
      self.robo.act('localize', 0, 0, 0)
      for y in range(0, self.gridsize):
         for x in range(0, self.gridsize):
            if self.cell_list[x][y]:
               self.c.delete(self.cell_list[x][y])
               self.cell_list[x][y] = 0
      
   def __init__(self, size):
      self.scale = 6.0
      self.robo = SaphiraRobot()
      self.gridsize = size # size * size cells
      self.gi = gridio.gridinterface(self.robo, self.gridsize, self.gridsize)
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

      while(1):
         self.update()
         
   def update(self):
      self.robo.update()
      self.gi.updategrid()
      self.draw()
      self.prompt()
      self.c.update()
      self.c.after(50)

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

   def draw(self):
      canvas = self.c

      for x in range(0, self.gridsize):
         for y in range(0, self.gridsize):
            occupancy = self.gi.getoccupancy(x, y)

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
            if self.cell_list[x][y]:
               canvas.itemconfigure(self.cell_list[x][y], \
                                    outline=rgb, fill=rgb)
            else:
               self.cell_list[x][y] = canvas.create_oval(
                  x * self.scale - self.scale/2.0,\
                  y * self.scale - self.scale/2.0,\
                  x * self.scale + self.scale/2.0,\
                  y * self.scale + self.scale/2.0,\
                  fill=rgb,\
                  outline=rgb)
     
if (__name__ == '__main__'):
   gt = GridTest(50)
   # when plotting 100/2 = 50 should be added to
   # center the points

      
