from OpenGL.Tk import *

class GeneralPlot:
   """
   A plot class.  Currently supports scrolling and freezing the graph
   at a point in time.  To be invoked by a plugin in pyro/plugins/plots.
   """
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
      """
      Initializer function.

      Required arguments:
      robot - the robot the sensors of which are to be graphed.
      brain - the brain of that robot.
      sensorList - a simple list of the sensor numbers that are to
        be polled by this plot.

      Optional arguments:
      sensorType - The type of sensors to be polled.  This is used in
        as an argument to robot.get(), so it must be accurate.  Deaults
        to 'sonar'
      name - Not really used. defaults to 'Plot'
      history - The number of timesteps to keep in memory.  Defaults to 1000
      stepLength - the amount of space (in pixels) that each timestep gets
        on the x axis.  Defaults to 2.
      minVal - The minimum value that the sensors will reach.  This is used as
        the minimum y value on the graph.  Defaults to 0.
      maxVal - The maximum value that the sensors will reach.  This is used as
        the ,aximum y value on the graph.  Defaults to 3.
      width - The displayed width of the graph (in pixels).  Defaults to 400.
      height - The displaed height of the graph (in pixels).  Defaults to 120.
      """
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
      self.maxHist = history - 1
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
      self.frozen = 0
      self.scrollInterval = 14.
      
<<<<<<< __init__.py
      #a hack to prevent a gap in the plot the first time
      #canvas.move is called in redraw
      self.firstMove = 1

      #setup Tk components
=======
      self.scrollhoriz = Scrollbar(self.win, orient="horiz",
                                   command=self.scroll)
      self.scrollhoriz.pack(side=BOTTOM,expand="yes",fill="both",padx=1,pady=1)
>>>>>>> 1.4
      self.canvas = Canvas(self.win, width=self.width, height=self.height,
                           scrollregion=(0, 0,
                                         history * stepLength, self.height),
<<<<<<< __init__.py
                           xscrollincrement=self.stepLength)
      yaxis = Canvas(self.win, width=20, height = self.height)
      yaxis.create_line(20, 0, 20, self.height, width=1, fill='black')
      yaxis.create_text(20, 0, text=str(self.dataMax), anchor=NE)
      yaxis.create_text(20, self.height, text=str(self.dataMin), anchor=SE)
      b1 = Button(self.win, text="<==", command=self.scrollLeft)
      self.freezeButton = Button(self.win, text="Freeze",
                                 command=self.freezePress)
      b3 = Button(self.win, text="==>", command=self.scrollRight)
=======
                           xscrollincrement=self.stepLength,
                           xscrollcommand=self.xposition)
      self.canvas.pack() 
>>>>>>> 1.4

      #Do the layout
      yaxis.grid(row=0, column=0)
      self.canvas.grid(row=0, column=1, columnspan=3)
      b1.grid(row=1, column=1, sticky=W)
      self.freezeButton.grid(row=1, column=2)
      b3.grid(row=1, column=3, sticky=E)

<<<<<<< __init__.py

=======
      #b1 = Button(self.win, text="<==", command=self.scrollLeft)
      #b1.pack(side=LEFT)
      #self.freezeButton = Button(self.win, text="Freeze", command=self.freezePress)
      #self.freezeButton.pack(anchor=S)

      #b3 = Button(self.win, text="==>", command=self.scrollRight)
      #b3.pack(side=RIGHT)

      #sbv = Scrollbar(self.win, command = "$c yview")

   def xposition(self, left, right):
      #print "LEFT=", left, "RIGHT=", right
      pass

   def scroll(self, amount):
      #print "Amount:", amount
      self.canvas.xview(SCROLL, int(amount) * 10, UNITS)
>>>>>>> 1.4

   def scrollLeft(self):
      """
      Cause the graph to scroll left by self.scrollInterval * stepLength
      units.  Called by the left scroll button.
      """
      self.canvas.xview(SCROLL, -self.scrollInterval, UNITS)
      self.freeze()

   def scrollRight(self):
      """
      Cause the graph to scroll right by self.scrollInterval * stepLength
      units.  Called by the right scroll button.
      """
      self.canvas.xview(SCROLL, self.scrollInterval, UNITS)
      self.freeze()

   def freeze(self):
      """
      Freeze the graph, ceasing to draw but still collecting data.
      """
      self.freezeButton["text"] = "Unfreeze"
      self.frozen = 1
                            
   def freezePress(self):
      """
      Called by the Freeze/Unfreeze button.  Toggle between the frozen
      and unfrozen states.  If the graph was frozen, Redraw the entire canvas,
      using the data that's been collected while the graph was frozen.
      """
      if self.frozen:
         #unfreeze
         
         #calclate the percentage of the entire scrollregion that should be
         #shown; add in the dataWindowSize because MOVETO moves that percentage
         #to the left of the region
         if self.lastHist == 0:
            end = 0.0
         else:
            end = 1.0 - float(self.dataWindowSize)/float(self.lastHist)

         if end < 0.0:
            end = 0.0
         self.canvas.xview(MOVETO, end)

         #redraw everything
         self.canvas.delete('data')
         
         for val in range(self.lastHist+1):
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
      """
      The meat of the graph, this function actually collects the data and
      draws it on the canvas.
      """
      if self.lastRun != self.brain.lastRun:
         self.lastRun = self.brain.lastRun
         if self.lastHist == self.maxHist:
            self.history = self.history[1:] + [[None]*len(self.sensorList)]
         else:
            self.lastHist += 1
            self.history += [[None]*len(self.sensorList)]
               

         for n in range(len(self.sensorList)):
            val = self.robot.get(self.sensorType, 
                                 'value', 
                                 self.sensorList[n])
            #Make sure the recived values are within the range to be
            #graphed.  If they're not, set them to the appropriate
            #extreme
            if val < self.dataMin:
               val = self.dataMin
            elif val > self.dataMax:
               val = self.dataMax
               
            self.history[self.lastHist][n] = val
            
         #Don't draw if the plot is frozen
         if not self.frozen:
            if self.lastHist < self.dataWindowSize:
               pass
            elif self.dataWindowSize <= self.lastHist < self.maxHist:
               self.canvas.xview(SCROLL, 1, UNITS)
            elif self.firstMove:
               self.firstMove = 0
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
            
               
