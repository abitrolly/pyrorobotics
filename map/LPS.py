# Local Perceptual Space

from pyro.brain import Brain
from pyro.gui.plot.matrix import Matrix
from pyro.map.occupancyGrid import occupancyGrid
from math import *

class LPS(Brain):

   def setup(self):
      self.widthMMeters = 7 * 1000
      self.heightMMeters = 7 * 1000
      self.cellSizeMMeters = .5 * 1000
      self.cols = self.widthMMeters / self.cellSizeMMeters
      self.rows = self.heightMMeters / self.cellSizeMMeters
      self.occupancyGrid = occupancyGrid( [[0.5 for col in range(self.cols)] for row in range(self.rows)] )
      self.getRobot().set('sonar', 'units', 'METERS')
      #self.startService('truth')

   def step(self):
      robot = self.getRobot()
      self.occupancyGrid.value = [[0.5 for col in range(self.cols)] for row in range(self.rows)]
      #robotOrigin = robot.dev.get_truth_pose() # x, y, th in mm
      for i in range(robot.get('sonar', 'count')):
         origin = robot.get('sonar', 'ox', i), robot.get('sonar', 'oy', i)
         dist = robot.get('sonar', 'value', i)
         angle = robot.get('sonar', 'th', i)
         if dist < 2.99:
            radius = sqrt(origin[0]*origin[0] + origin[1]*origin[1])
            hyp = radius + (dist * 1000)
            xhit = cos(angle) * hyp 
            yhit = sin(angle) * hyp
            print i, origin, dist, radius, xhit, yhit
            self.setGrid(xhit, yhit, label = "%s" % i)

      self.occupancyGrid.redraw(self.occupancyGrid.value)

      for i in range(robot.get('sonar', 'count')):
         origin = robot.get('sonar', 'ox', i), robot.get('sonar', 'oy', i)
         dist = robot.get('sonar', 'value', i)
         angle = robot.get('sonar', 'th', i)
         radius = sqrt(origin[0]*origin[0] + origin[1]*origin[1])
         hyp = radius + (dist * 1000)
         xhit = cos(angle) * hyp 
         yhit = sin(angle) * hyp
         print i, origin, dist, radius, xhit, yhit
         self.setLabel(xhit, yhit, label = "%s" % i)


   def setLabel(self, xmm, ymm, value = 1.0, label = ""):
      center = self.widthMMeters / 2.0, self.heightMMeters / 2.0
      posX = int((center[0] + xmm) / self.cellSizeMMeters)
      posY = int((center[1] + ymm) / self.cellSizeMMeters)
      self.occupancyGrid.canvas.create_text(posX * self.occupancyGrid.xScale,
                                            posY * self.occupancyGrid.yScale,
                                            tag = "cell",
                                            text = label, fill = "yellow")
   def setGrid(self, xmm, ymm, value = 1.0, label = ""):
      center = self.widthMMeters / 2.0, self.heightMMeters / 2.0
      posX = int((center[0] + xmm) / self.cellSizeMMeters)
      posY = int((center[1] + ymm) / self.cellSizeMMeters)
      self.occupancyGrid.value[posY][posX] = value
         
def INIT(engine):
   return LPS('LPSBrain', engine)
      
