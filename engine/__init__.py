# Engine class; main controller

import time
import sys
import pyro.gui.console as console
import pyro.system as system
import pyro.gui.drawable as drawable

class Engine(drawable.Drawable):
   def __init__(self, robotfile = None, brainfile = None, simfile = None,
                brainargs=[], config = {}, camerafile = 0):
      drawable.Drawable.__init__(self,'engine')
      self.robot = 0
      self.brain = 0
      self.plot = []
      if brainfile != None:
         self.brainfile = brainfile
      else:
         self.brainfile = ''
      if robotfile != None:
         self.robotfile = robotfile
      else:
         self.robotfile = ''
      if camerafile != None:
         self.camerafile = camerafile
      else:
         self.camerafile = ''
      if simfile != None:
         self.simfile = simfile
      else:
         self.simfile = ''
      self.brainargs = brainargs
      self.config = config
      if self.simfile:
         self.loadSimulator(self.simfile)
      if self.robotfile:
         self.loadRobot(self.robotfile)
         if self.camerafile:
            self.loadCamera(self.camerafile)

   def postinit(self):
      if self.brainargs != [] and self.brainfile:
         self.loadBrain(self.brainfile, self.brainargs)
      elif self.brainfile:
         self.loadBrain(self.brainfile)

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
      print "Loading.",
      sys.stdout.flush()
      time.sleep(1)
      print ".",
      sys.stdout.flush()
      time.sleep(1)
      print ".",
      sys.stdout.flush()
      time.sleep(1)
      print "."
      sys.stdout.flush()

   def loadPlot(self,file):
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.plot.append(system.loadINIT(file, self.robot, 0, self.brain))
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/plots/' + file): 
         self.plot.append(system.loadINIT(os.getenv('PYRO') + \
                                          '/plugins/plots/' + file, \
                                          self.robot, 0, self.brain))
      else:
         raise 'Plot file not found: ' + file
      console.log(console.INFO,'Loaded ' + file)
      #self.append(self.robot)

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

   def loadCamera(self,file):
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.camerafile = file
         self.robot.camera = system.loadINIT(file)
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/cameras/' + file): 
         self.camerafile = os.getenv('PYRO') + '/plugins/cameras/' + file
         self.robot.camera = system.loadINIT(os.getenv('PYRO') + \
                                      '/plugins/cameras/' + file)
      else:
         raise 'Camera file not found: ' + file
      self.robot.camera.makeWindow()
      console.log(console.INFO,'Loaded ' + file)
      #self.append(self.robot.camera)

   def loadBrain(self,file, args=None):
      if self.robot is 0:
         raise 'No robot loaded when loading brain'
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.brainfile = file
         if args:
            self.brain = system.loadINIT(file, self.robot, args=args)
         else:
            self.brain = system.loadINIT(file, self.robot)
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/brains/' + file): 
         self.brainfile = os.getenv('PYRO') + '/plugins/brains/' + file
         if args:
            self.brain = system.loadINIT(os.getenv('PYRO') + \
                                         '/plugins/brains/' + file,
                                         self.robot, args=args)
         else:
            self.brain = system.loadINIT(os.getenv('PYRO') + \
                                         '/plugins/brains/' + file, self.robot)
      else:
         raise 'File not found: ' + file
      console.log(console.INFO,'Loaded ' + file)
      # FIX: currently, brain is not a drawable
      #self.append(self.brain)

   def freeBrain(self):
      if self.brain != 0:
         self.brain.pleaseQuit()
      
   def freeRobot(self):
      self.freeBrain()
      if self.robot != 0:
         self.robot.disconnect()

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
      
