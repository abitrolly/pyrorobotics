from OpenGL.Tk import *

class GeneralPlot:
   def __init__(self,
                robot,
                brain,
                sensorList,
                sensorType='sonar',
                name='Plot',
                history=1000,
                stepLength=2,
                minVal=0,
                maxVal=3,
                width=400,
                height=120):
      
      self.win = Tk()
      self.robot = robot
      self.brain = brain
      self.name = name
      self.stepLength = stepLength
      self.dataMin = minVal
      self.dataMax = maxVal
      self.win.wm_title("PyroPlot: %s" % self.name)
      
      self.sensorType = sensorType
      self.sensorList = sensorList
      self.history = []
      self.maxHist = history
      self.lastHist = -1 #The last used value in history
      self.lastRun = 0
      self.colors = ['blue', 'red', 'tan', 'yellow', 'orange', \
                     'black', 'azure', 'beige', 'brown', 'coral', \
                     'gold', 'ivory', 'moccasin', 'navy', 'salmon', \
                     'tan', 'ivory']

      self.width = width
      self.height = height

      self.dataWindowSize = self.width/self.stepLength
      if self.dataWindowSize < 1:
         self.ataWindowSize = 1
      
      self.canvas = Canvas(self.win, width=self.width, height=self.height,
                           scrollregion=(0, 0,
                                         history * stepLength, self.height))
#                           xScrollIncrement=self.stepLength
      self.canvas.pack()
      self.dump.pack()

   def dump(self):
      print self.history
                         
   
   def convertVal(self, value):
      """
      Given a sensor value, convert it to coordinates using
      dataMin, dataMax, and height
      """
      #this is a hack to deal with the first one
      if value == None:
         return 0
      
      if value > self.dataMax:
         value = self.dataMax
      retval = int(round((value / (self.dataMax - self.dataMin)) * self.height))
      return retval

   def redraw(self, options):
      if self.lastRun != self.brain.lastRun:
         self.lastRun = self.brain.lastRun
         if self.lastHist == self.maxHist - 1:
            self.history = self.history[1:] + [[None]*len(self.sensorList)]
         else:
            self.lastHist += 1
            self.history += [[None]*len(self.sensorList)]
         

         for n in range(len(self.sensorList)):
            self.history[self.lastHist][n] = self.robot.get(self.sensorType, 
                                                       'value', 
                                                       self.sensorList[n])
         if self.lastHist < self.dataWindowSize:
            for n in range(len(self.sensorList)):
               self.canvas.create_line((self.lastHist-1)*self.stepLength,
                                       self.convertVal(self.history[self.lastHist-1][n]),
                                       self.lastHist*self.stepLength,
                                       self.convertVal(self.history[self.lastHist][n]),
                                       tags = 'data',
                                       width = 2,
                                       fill = self.colors[n])
               
         else:
            self.canvas.xview(SCROLL, 1, UNITS)
            self.canvas.delete('data')
            for val in range(self.lastHist - self.dataWindowSize, self.lastHist):
               for n in range(len(self.sensorList)):
                  self.canvas.create_line((val-1)*self.stepLength,
                                          self.convertVal(self.history[val-1][n]),
                                          val*self.stepLength,
                                          self.convertVal(self.history[val][n]),
                                          tags = 'data',
                                          width = 2,
                                          fill = self.colors[n])
            
               
