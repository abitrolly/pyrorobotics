from Tkinter import *
from string import *

class GeneralPlot:
   """
   A plot class.  Currently supports scrolling and freezing the graph
   at a point in time.  To be invoked by a plugin in pyro/plugins/plots.
   """
   def __init__(self,
                robot,
                brain,
                sensorList,
                sensorType='range',
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
      sensorType - The type of sensors to be polled. 
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
      self.win = Toplevel()
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
      self.scrollInterval = 14
      
      #a hack to prevent a gap in the plot the first time
      #canvas.move is called in redraw
      self.firstMove = 1

      #setup Tk components

      self.scrollhoriz = Scrollbar(self.win, command=self.scroll, orient=HORIZONTAL)
      self.canvas = Canvas(self.win, width=self.width, height=self.height,
                           scrollregion=(0, 0,
                                         history * stepLength, self.height),
                           xscrollincrement=self.stepLength,
                           xscrollcommand=self.scrollhoriz.set)
      self.canvas.create_line(0, self.height-1,
                              history * stepLength, self.height-1,
                              width=1, fill='black')
      yaxis = Canvas(self.win, width=20, height = self.height)
      yaxis.create_line(20, 0, 20, self.height, width=1, fill='black')
      yaxis.create_text(20, 0, text=str(self.dataMax), anchor=NE)
      yaxis.create_text(20, self.height, text=str(self.dataMin), anchor=SE)
#        self.xaxis = Canvas(self.win, width=self.width, height=20,
#                            scrollregion=(0, 0,
#                                          history * stepLength, self.height),
#                            xscrollincrement=self.stepLength,
#                            xscrollcommand=self.scrollhoriz.set)
#        self.xaxis.create_line(0, 3, history * stepLength, 3,
#                               width=1, fill='black')
#        for x in range(0, history * stepLength, 30 * stepLength):
#           #draw ticks every thirty steps
#           self.xaxis.create_line(x, 0, x, 20, width=1, fill='black')
#           self.xaxis.create_text(x, 5, text=str(x), anchor=NE)
#           self.canvas.create_line(x, 0, x, self.height, width=1, fill='gray')
      self.freezeButton = Button(self.win, text="Freeze",
                                 command=self.freezePress)

      #Do the layout
      yaxis.grid(row=0, column=0)
      self.canvas.grid(row=0, column=1, columnspan=3)
      #to put the next line back in, make sure to add one to the
      #row argument on the next two lines
#      self.xaxis.grid(row=1, column=1, columnspan=3)
      self.scrollhoriz.grid(row=1, column=1, columnspan=3, sticky=W+E)
      self.freezeButton.grid(row=2, column=2)

   def saveToFile(self, fname):
      """
      Writes the plot to file fname.
      
      File Format:
      dataMin
      dataMax
      Sensor1 Sensor2 Sensor3...Sensorn
      val1 val2 val3...valn
      val1 val2 val3...valn
      .
      .
      .
      val1 val2 val3...valn
      """
      try:
         file = open(fname, "w")
      except:
         raise "Save: Error opening file " + fname

      file.write(str(self.dataMin + "\n"))
      file.write(str(self.dataMax + "\n"))
      for n in range(len(self.sensorList)):
         file.write(str(self.sensorList[n]) + " ")
      file.write("\n")
      for n in range(len(self.history)):
         for m in range(len(self.sensorList)):
            file.write(str(self.history[n][m] + " "))
         file.write("\n")

      file.close()

   def loadFromFile(self, fname):
      """
      Loads a plot from file fname
      """

      try:
         file = open(fname, "r")
      except:
         raise "Load: Error opening file " + fname

      self.dataMin = int(file.readline())
      self.dataMax = int(file.readline())
      self.sensorList = map(lambda(x): int(x),
                            split(strip(file.readline()), " "))
      self.history = []
      line = strip(file.readline())
      while line != "":
         self.history.append(map(lambda(x): float(x), split(line, " ")))
         line = strip(file.readline())

      file.close() 
   
   def scroll(self, *args):
      """
      This method intercepts the scroll message from the scrollbar.  It
      calls freeze(), and, if one of the arrow buttons on the scrollbar
      was pressed, it increases the amount by which the canvas is scrolled.
      """
      self.freeze()
      if len(args) == 3:
         #One of the arrow buttons was pressed
         #multiply args[1] (which will be 1 or -1) by the deisred scroll
         #interval
         self.canvas.xview(args[0], int(args[1])*self.scrollInterval, args[2])
      else:
         #otherwise just pass the arguments on to xview
         self.canvas.xview(*args)

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
               self.canvas.scroll(SCROLL, 1, UNITS)
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
            
               
