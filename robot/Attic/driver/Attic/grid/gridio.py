import math, sys
import pyro.gui.console as console
from spg import *

class gridinterface:
   def __init__(self, robot, grid_size, lgrid_size):
      self.robot = robot
      self.grid_size = grid_size 
      self.grid = new_SpacePerceptionGrid(grid_size, grid_size)
      # lgrid_size is local grid size
      ###self.lgrid_size = grid_size # should depend on a sensor
      self.lgrid_size = lgrid_size # should depend on a sensor
      self.local_grid = new_SpacePerceptionGrid(self.lgrid_size, \
                                                self.lgrid_size)
      self.lgrid_ox = 0
      self.lgrid_oy = 0

      self.scale = 5.0

      # test
      self.counter = 0



   def updategrid(self):
      robo = self.robot

      for s in range(0, self.robot.get('sonar', 'count')):
         hit = robo.get('sonar', 'flag', s)
         if hit == 0: # old data
            continue
         # else it is a hit, or open
         _x0 = robo.get('sonar', 'ox', s) 
         _y0 = robo.get('sonar', 'oy', s) 
         _x1 = robo.get('sonar', 'x', s)  
         _y1 = robo.get('sonar', 'y', s)  

         arc = robo.get('sonar', 'arc', s) * 3.0 

         """
         c0 = coord(robo, _x0, _y0, "local") 
         c1 = coord(robo, _x1, _y1, "local") 
         x0 = c0.getgx() * self.scale 
         y0 = c0.getgy() * self.scale 
         x1 = c1.getgx() * self.scale 
         y1 = c1.getgy() * self.scale 


         if hit == 2:  # then it is all open 
            print "beyond range = (%f, %f)" % (x1, y1) # mark with no hit 
         SpacePerceptionGrid_update(self.grid, self.grid_size / 2.0 + x0, \
                                    self.grid_size / 2.0 + y0, \
                                    self.grid_size / 2.0 + x1, \
                                    self.grid_size / 2.0 + y1, \
                                    arc, 1, hit != 2) 
         """

         # for local grid
         rx = robo.get('robot', 'x') * self.scale 
         ry = robo.get('robot', 'y') * self.scale
         diff_x = rx - self.lgrid_ox
         diff_y = ry - self.lgrid_oy
         thr = - robo.get('robot', 'thr')

         xx0 = (_x0 * math.cos(thr) - \
                _y0 * math.sin(thr)) * self.scale + diff_x
         yy0 = (_x0 * math.sin(thr) + \
                _y0 * math.cos(thr)) * self.scale + diff_y
         xx1 = (_x1 * math.cos(thr) - \
                _y1 * math.sin(thr)) * self.scale + diff_x
         yy1 = (_x1 * math.sin(thr) + \
                _y1 * math.cos(thr)) * self.scale + diff_y 

         SpacePerceptionGrid_update(self.local_grid, \
                                    self.lgrid_size / 2.0 + xx0, \
 self.lgrid_size / 2.0 + yy0, \
                                    self.lgrid_size / 2.0 + xx1, \
                                    self.lgrid_size / 2.0 + yy1, \
                                    arc, 1, hit != 2)

      is_reset = 0
      if (self.counter > 0):
        updated_region = self.resetlocal()
        is_reset = 1
        self.counter = 0
      self.counter += 1

      #print "updated."
      if is_reset:
         return updated_region
      else:
         return 0

   def getoccupancy(self, cell_x, cell_y):
      return SpacePerceptionGrid_get(self.grid, cell_x, cell_y)
   def getlocaloccupancy(self, cell_x, cell_y):
      return SpacePerceptionGrid_get(self.local_grid, cell_x, cell_y)
   def reset(self):
      return SpacePerceptionGrid_reset(self.grid)
   def resetlocal(self):
      last_x = self.lgrid_ox
      last_y = self.lgrid_oy
      self.lgrid_ox = self.robot.get('robot', 'x') * self.scale
      self.lgrid_oy = self.robot.get('robot', 'y') * self.scale
      dx = self.lgrid_ox - last_x
      dy = self.lgrid_oy - last_y

      # get pointers of arrays from the c++ module
      src = SpacePerceptionGrid_getref(self.local_grid)
      dest = SpacePerceptionGrid_getref(self.grid)

      # starting point of copy
      begin_x = - (last_x + self.lgrid_size / 2.0) + self.grid_size / 2.0
      begin_y = - (last_y + self.lgrid_size / 2.0) + self.grid_size / 2.0
      #print begin_x, begin_y

      # pass pointers and parameters to c++ module

      SpacePerceptionGrid_copyregion(self.local_grid, \
                                     src, dest, begin_x, begin_y, \
                                     self.lgrid_size, self.lgrid_size)

      # clear local grid
      ###SpacePerceptionGrid_reset(self.local_grid)
      
      # here, save some data and overwrite
      SpacePerceptionGrid_recenter(self.local_grid, \
                                   dx, dy)

      return (begin_x, begin_y, self.lgrid_size, self.lgrid_size)

   def decay(self):
      SpacePerceptionGrid_decay(self.grid)

   def getclosest(self):
      # returns the closest thing in the global grid
      pass

   def getopendirection(self):
      # returns a vector?
      pass

class coord:
   def __init__(self, robot, x, y, system="local"):
      self.gxy = (0, 0)
      self.lxy = (0, 0)
      self.robot = robot
      if system == "local":
         self.lxy = (x, y)
         self.gxy = self.toGlobal(self.lxy)
      elif system == "global":
         self.gxy = (x, y)
         self.lxy = self.toLocal(self.gxy)
      else:
         console.log(console.WARNING, "coord: warning! defaults to global")
         self.gxy = (x, y)
         self.lxy = self.toLocal(self.gxy)
         
   def getgx(self): return self.gxy[0]
   def getgy(self): return self.gxy[1]
   def getlx(self): return self.lxy[0]                 
   def getly(self): return self.lxy[1]

   def toGlobal(self, lxy):
      robo = self.robot
      (local_x, local_y) = (lxy[0], lxy[1])
      robot_th = robo.get('robot', 'thr')
      robot_x  = robo.get('robot', 'x')
      robot_y  = robo.get('robot', 'y')
      global_x  = - robot_y + local_x * math.cos(robot_th) - \
                  local_y * math.sin(robot_th)
      global_y  = - robot_x + local_x * math.sin(robot_th) + \
                  local_y * math.cos(robot_th)
      return (global_x, global_y)

   def toLocal(self, gxy):
      robo = self.robot
      (global_x, global_y) = (gxy[0], gxy[1])
      robot_th = robo.get('robot', 'thr')
      robot_x  = robo.get('robot', 'x')
      robot_y  = robo.get('robot', 'y')
      local_x  = (global_x - robot_x) * math.cos(- robot_th) - \
                 (global_y - robot_y) * math.sin(- robot_th)
      local_y  = (global_x - robot_x) * math.sin(- robot_th) + \
                 (global_y - robot_y) * math.cos(- robot_th)
      return (local_x, local_y)
   
