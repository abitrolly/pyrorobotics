# Engine class; main controller

import time
import sys
import pyro.gui.console as console
import pyro.system as system
import pyro.gui.drawable as drawable

class Engine(drawable.Drawable):
   def __init__(self, robotfile = None, brainfile = None, simfile = None,
                pyroargs=[], config = {}, worldfile = 0, services = 0):
      drawable.Drawable.__init__(self,'engine')
      self.robot = 0
      self.brain = 0
      self.gui = None
      self.view = []
      if brainfile != None:
         self.brainfile = brainfile
      else:
         self.brainfile = ''
      if robotfile != None:
         self.robotfile = robotfile
      else:
         self.robotfile = ''
      if worldfile != None:
         self.worldfile = worldfile
      else:
         self.worldfile = ''
      if simfile != None:
         self.simfile = simfile
      else:
         self.simfile = ''
      self.args = pyroargs
      self.config = config
      if self.simfile:
         self.loadSimulator(self.simfile, self.worldfile)
      if self.robotfile:
         self.loadRobot(self.robotfile)
         if services != ['']:
            self.robot.startServices(services)
      if self.brainfile:
         self.loadBrain(self.brainfile)
         time.sleep(2)

   def reset(self):
      self.pleaseStop()
      time.sleep(.1) # give it time to stop
      if self.brain is not 0:
         self.brain.pleaseQuit()
         time.sleep(.1) # give it time to stop
         #self.robot = system.loadINIT(self.robotfile, redo = 1)
         try:
            self.brain.destroy()
         except:
            print "I was unable to properly destroy the brain"
         self.brain = system.loadINIT(self.brainfile, self, 1)

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

   def loadSimulator(self, file, worldfile):
      console.log(console.INFO,'Loading ' + file)
      import os, string
      options = string.split(file)
      guiflag = ''
      simulatorName = file.split('/')[-1]
      if system.file_exists(worldfile):
         pass # leave it alone
      elif system.file_exists( os.getenv('PYRO') + \
                               '/plugins/worlds/%s/%s' % (simulatorName, worldfile)):
         worldfile = os.getenv('PYRO') + \
                     '/plugins/worlds/%s/%s' % (simulatorName, worldfile)
      if self.config.get("pyro", "gui") == 'TTY':
         guiflag = '-g'
      if system.file_exists(options[0]):
         os.system(file + " " + guiflag + " " + worldfile + " &")
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/simulators/' + options[0]):
         os.system(os.getenv('PYRO') + '/plugins/simulators/' + file + \
                   " " + guiflag + " " + worldfile + " &")
      else:
         raise 'Simulator file not found: ' + file
      console.log(console.INFO,"Loaded '%s' with world file '%s'" %(file, worldfile))
      print "Loading.",
      sys.stdout.flush()
      time.sleep(1)
      print ".",
      sys.stdout.flush()

   def loadView(self,file):
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.view.append(system.loadINIT(file, self, 0, self.brain))
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/views/' + file): 
         self.view.append(system.loadINIT(os.getenv('PYRO') + \
                                          '/plugins/views/' + file, \
                                          self.robot, 0, self.brain))
      else:
         raise 'View file not found: ' + file
      console.log(console.INFO,'Loaded ' + file)
      #self.append(self.robot)

   def loadRobot(self,file):
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.robot = system.loadINIT(file)
         self.robotfile = file
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/robots/' + file): 
         self.robot = system.loadINIT(os.getenv('PYRO') + \
                                      '/plugins/robots/' + file)
         self.robotfile = os.getenv('PYRO') + '/plugins/robots/' + file
      else:
         raise 'Robot file not found: ' + file
      console.log(console.INFO,'Loaded ' + file)
      self.append(self.robot)

   def loadMap(self,file):
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.robot.map.append( system.loadINIT(file, self) )
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/maps/' + file): 
         self.robot.map.append( system.loadINIT(os.getenv('PYRO') + \
                                                '/plugins/maps/' + \
                                                file, self))
      else:
         raise 'Map file not found: ' + file
      console.log(console.INFO,'Loaded ' + file)


   def loadBrain(self,file):
      if self.robot is 0:
         raise 'No robot loaded when loading brain'
      import os
      console.log(console.INFO,'Loading '+file)
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.brain = system.loadINIT(file, self)
         self.brainfile = file
      elif system.file_exists(os.getenv('PYRO') + \
                              '/plugins/brains/' + file): 
         self.brain = system.loadINIT(os.getenv('PYRO') + \
                                      '/plugins/brains/' + file, self)
         self.brainfile = os.getenv('PYRO') + '/plugins/brains/' + file
      else:
         raise 'File not found: ' + file
      console.log(console.INFO,'Loaded ' + file)

   def freeBrain(self):
      if self.brain != 0:
         self.brain.pleaseQuit()
      
   def freeRobot(self):
      self.freeBrain()
      if self.robot != 0:
         self.robot.disconnect()

   def shutdown(self):
      self.freeRobot()
         
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
      if self.robot is not 0:
         self.robot.stop()

   def _draw(self,options,renderer):
	pass # overload, if you want to draw it
      
   def destroyBrain(self):
      if self.brain is not 0:
         try:
            self.brain.destroy()
         except:
            print "I was unable to properly destroy the brain"

   def getGUI(self):
      return self.gui
