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
                     'green', 'ivory']

      self.width = width
      self.height = height

      self.dataWindowSize = self.width/self.stepLength
      if self.dataWindowSize < 1:
         self.dataWindowSize = 1
      
      self.canvas = Canvas(self.win, width=self.width, height=self.height,
                           scrollregion=(0, 0,
                                         history * stepLength, self.height),
                           xscrollincrement=self.stepLength)
      self.canvas.pack()

      self.frozen = 0

      b1 = Button(self.win, text="<==", command=self.scrollLeft)
      b1.pack(side=LEFT)
      self.freezeButton = Button(self.win, text="Freeze", command=self.freezePress)
      b3 = Button(self.win, text="==>", command=self.scrollRight)
      b3.pack(side=RIGHT)
      self.freezeButton.pack(anchor=S)


   def scrollLeft(self):
      self.canvas.xview(SCROLL, -10, UNITS)
      self.freeze()

   def scrollRight(self):
      self.canvas.xview(SCROLL, 10, UNITS)
      self.freeze()

   def freeze(self):
      self.freezeButton["text"] = "Unfreeze"
      self.frozen = 1
                            
   def freezePress(self):
      if self.frozen:
         #unfreeze
         self.canvas.xview(MOVETO, 1.0)
         self.canvas.delete('data')
         for val in range(self.lastHist):
            for n in range(len(self.sensorList)):
               self.canvas.create_line((val-1)*self.stepLength,
                                       self.convertVal(self.history[val-1][n]),
                                       val*self.stepLength,
                                       self.convertVal(self.history[val][n]),
                                       tags = 'data',
                                       width = 2,
                                       fill = self.colors[n])
         self.freezeButton["text"] = "Freeze"
         self.frozen = 0
      else:
         self.freeze()
         
   
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
         if not self.frozen:
            if self.lastHist < self.dataWindowSize:
               pass
            elif self.dataWindowSize <= self.lastHist < self.maxHist - 1:
               self.canvas.xview(SCROLL, 1, UNITS)
            else:
               self.canvas.move('data', -self.stepLength, 0)
               
            for n in range(len(self.sensorList)):
               self.canvas.create_line((self.lastHist-1)*self.stepLength,
                                       self.convertVal(self.history[self.lastHist-1][n]),
                                       self.lastHist*self.stepLength,
                                       self.convertVal(self.history[self.lastHist][n]),
                                       tags = 'data',
                                       width = 2,
                                       fill = self.colors[n])
            
               
