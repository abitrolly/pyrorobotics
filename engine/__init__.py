# Engine class; main controller

import time

import pyro.gui.console as console
import pyro.system as system
import pyro.gui.drawable as drawable

class Engine(drawable.Drawable):
   def __init__(self, robotfile = 0, brainfile = 0, simfile = 0):
      drawable.Drawable.__init__(self,'engine')
      self.robot = 0
      self.brain = 0
      self.brainfile = ''
      self.robotfile = ''
      if simfile != 0:
         self.loadSimulator(simfile)
      if robotfile != 0:
         self.loadRobot(robotfile)
      if brainfile != 0:
         self.loadBrain(brainfile)

   def reset(self):
      self.pleaseStop()
      time.sleep(.1) # give it time to stop
      if self.brain:
         self.brain.pleaseQuit()
         time.sleep(.1) # give it time to stop
         #self.robot = system.loadINIT(self.robotfile, redo = 1)
         self.brain = system.loadINIT(self.brainfile, self.robot, 1)

   def resetFirstAttempts(self):
      self.pleaseStop()
      if self.robotfile:
         file = self.robotfile[0:-3] # strip off .py
         #file = file.replace('/', '.')
         file = file.split('/')
         file = "pyro." + file[-3] + "." + file[-2] + "." + file[-1]
         print file
         exec( "reload(" + file + ")")
      if self.brainfile:
         file = self.brainfile[0:-3] # strip off .py
         #file = file.replace('/', '.')
         file = file.split('/')
         file = "pyro." + file[-3] + "." + file[-2] + "." + file[-1]
         print file
         exec( "reload(" + file + ")")
         #exec( "reload(" + file + ")")
         #reload(file)
         #reload(self.brainfile)

   def loadSimulator(self,file):
      console.log(console.INFO,'Loading ' + file)
      import os, string
      options = string.split(file)
      if system.file_exists(options[0]):
         os.system(file + " &")
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/simulators/' + options[0]):
         os.system(os.getenv('PYRO') + '/plugins/simulators/' + file + " &")
      else:
         raise 'Simulator file not found: ' + file
      console.log(console.INFO,'Loaded ' + file)

   def loadRobot(self,file):
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.robotfile = file
         self.robot = system.loadINIT(file)
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/robots/' + file): 
         self.robotfile = os.getenv('PYRO') + '/plugins/robots/' + file
         self.robot = system.loadINIT(os.getenv('PYRO') + \
                                      '/plugins/robots/' + file)
      else:
         raise 'Robot file not found: ' + file
      console.log(console.INFO,'Loaded ' + file)
      self.append(self.robot)

   def loadBrain(self,file):
      if self.robot is 0:
         raise 'No robot loaded when loading brain'
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.brainfile = file
         self.brain = system.loadINIT(file, self.robot)
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/brains/' + file): 
         self.brainfile = os.getenv('PYRO') + '/plugins/brains/' + file
         self.brain = system.loadINIT(os.getenv('PYRO') + \
                                      '/plugins/brains/' + file, self.robot)
      else:
         raise 'File not found: ' + file
      console.log(console.INFO,'Loaded ' + file)
      # FIX: currently, brain is not a drawable
      #self.append(self.brain)

   def freeBrain(self):
      #print "freeBrain!"
      if self.brain != 0:
         #print "freeBrain running!"
         self.brain.pleaseQuit()
         #time.sleep(1)
         #self.brain = 0
         #del self[self.index(self.brain)]
      
   def freeRobot(self):
      self.freeBrain()
      #print "freeRobot!"
      if self.robot != 0:
         #print "freeRobot running!"
         self.robot.disconnect()
         #self.robot = 0
         #del self[self.index(self.robot)]

   def shutdown(self):
      self.freeRobot()
      print "shuting down..."
         
   def tryToConnect(self):
      if (self.robot is 0) or (self.brain is 0):
         print "Need to have a robot and brain connected!"
         return #no go, not enough parts to make frankie go

   def pleaseRun(self, callback = 0):
      if self.brain is not 0:
         self.brain.pleaseRun(callback)

   def pleaseStep(self):
      if self.brain is not 0:
         self.brain.pleaseStep()
         time.sleep(.5) # arbitrary time to allow it to do something
         self.robot.act('move', 0, 0)

   def pleaseStop(self):
      if self.brain is not 0:
         self.brain.pleaseStop()
         time.sleep(.5) # FIX: because there is no queue for commands
      if self.robot is not 0:
         self.robot.stop()

   def _draw(self,options,renderer):
	pass # overload, if you want to draw it
      
