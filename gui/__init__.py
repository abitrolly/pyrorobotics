import os
import sys
import signal
import time
import string
from pyro.gui.drawable import *
from pyro.gui.renderer.tty import *
from pyro.gui.renderer.streams import *
from pyro.system.version import version as version
from pyro.system import help, usage, about

class gui(Drawable):
   """
   This is the base class for a gui.
   """
   
   def __init__(self, name = 'abstract gui', options = {}, engine = 0):
      """
      Child classes should do initialization pertaining to the creation
      of the GUI in the constructor.
      """
      Drawable.__init__(self, name, options)
      self.engine = engine
      self.prevsighandler = signal.signal(signal.SIGINT, self.INThandler)
      self.append(self.engine)  # append engine to drawable

   def init(self):
      pass
      
   def run(self, command = []):
      """
      Child classes should do the beef of what they do right here.
      """
      done = 0
      print "========================================================="
      print "Pyro Robotics Control System, (c) 2002, D.S. Blank"
      print "Version " + version()
      print "========================================================="
      while done is not 1:
         print "Pyro > ", 
         if len(command) > 0:
            print command[0],
            retval = command[0].strip()
            command = command[1:]
         else:
            retval = sys.stdin.readline()
         print ""
         if retval == '':
            done = 1
            continue
         done = self.processCommand(retval)

   def processCommand(self, retval):
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      retval = retval.strip()
      if retval == "run":
         print "Running in thread..."
         self.engine.pleaseRun() # pass in callback, or not
         # self.engine.pleaseRun(self.redraw) # pass in callback
      elif retval == "info":
         print "-------------------------------------------------------------"
         print "Brain file:\t%s" % self.engine.brainfile
         print "Brain:\t\t%s" % self.engine.brain
         print "Robot:\t\t%s" % self.engine.robot
         print "-------------------------------------------------------------"
      elif retval == "help":
         help()
      elif retval == "usage":
         usage()
      elif retval == "update":
         if self.engine.robot != 0:
            self.engine.robot.update()
            print "Done!"
         else:
            print "Define a robot first!"
      elif retval == "about":
         about()
      elif retval == "reload":
         self.engine.reset()
      elif retval == "load camera":
         self.loadCamera()
      elif retval == "load robot":
         self.loadRobot()
      elif retval == "load brain":
         self.loadBrain()
      elif retval == "stop":
         self.engine.pleaseStop()
         print "Stopped!"
      elif retval == "quit" or retval == "exit" or retval == "bye":
         self.done = 1
         return 1
      elif len(retval) > 2 and retval[0] == "%":
         exp = string.strip(retval[1:])
         os.system(exp)
      elif retval == "edit":
         if self.engine.brainfile != '':
            if os.getenv("EDITOR"): 
               editor = os.getenv("EDITOR")
            else:
               editor = "emacs"
            os.system("%s %s" % (editor, self.engine.brainfile))
            print "Reloading..."
            self.engine.reset()
         else:
            print "Need to load a brain first"
      else:
         # elif len(retval) > 0 and retval[0] == "!":
         exp1 = "print " + string.strip(retval)
         exp2 = string.strip(retval)
         brain = self.engine.brain
         robot = self.engine.robot
         engine = self.engine
         gui = self
         print "> " + string.strip(retval) + " =>",
         try:
            exec exp1
         except:
            try:
               exec exp2
               print ''
            except:
               import sys
               print sys.exc_value
         #print "Unknown command: '" + retval + "'" sys.exc_type
      return 0

   def redraw(self):
      # FIX: this is way awkward:
      f = GenericStream()
      r = StreamRenderer(f)
      self.draw({}, r) # get data from robot, other things
      f.close()
      s = StreamTranslator(f, TTYRenderer())
      s.process()
      f.close()

   def _draw(self,options,renderer):
      """
      If the gui need draw something itself it should go here.
      """
      #render world
      #renderer.xformPush()
      renderer.color((1, 1, 1))
      renderer.rectangle((-10, -10, 0), (10, -10, 0), (10, 10, 0))
      #renderer.xformPop()
      #print "Redraw gui..."

   def makeMenu(self,name,commands):
      """ Could bind a key right here ^1, ^2, ^3..."""
      pass

   def fileloaddialog(self, type, skel):
      """ Could read a line from user """
      print "\nFilename: ",
      retval =  sys.stdin.readline()
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      return retval

   def cleanup(self):
      print "Cleaning up..."
      self.done = 1
      if self.engine != 0:
         self.engine.shutdown()
      print "Exiting!"
      sys.exit(1)

   def stepEngine(self):
      self.engine.pleaseStep()
      self.inform("Step done!")

   def runEngine(self):
      self.engine.pleaseRun()
      self.inform("Running...")

   def stopEngine(self): # stop!
      self.engine.pleaseStop()
      self.inform("Stopped!")

   def stopTranslate(self):
      self.engine.robot.step('ST')

   def stopRotate(self):
      self.engine.robot.step('SR')

   def stepForward(self):
      self.engine.robot.step('F')

   def stepBack(self):
      self.engine.robot.step('B')

   def stepLeft(self):
      self.engine.robot.step('L')

   def stepRight(self):
      self.engine.robot.step('R')

   def resetEngine(self):
      self.engine.reset()
      
   def loadBrain(self):
      f = self.fileloaddialog("brains","*.py")
      self.redraw()
      if f != '':
         #try:
         self.engine.loadBrain(f)
         self.redraw()
         #except:
         #raise "Error loading Brain File"

   def loadPlot(self):
      f = self.fileloaddialog("plots","*.py")
      self.redraw()
      if f != '':
         self.engine.loadPlot(f)
         self.redraw()

   def freeBrain(self):
      self.engine.freeBrain()

   def loadSim(self):
      f = self.fileloaddialog("simulators","*")
      self.redraw()
      if f != '':
         import os
         os.system(f + " &")
         
   def loadRobot(self):
      f = self.fileloaddialog("robots","*.py")
      self.redraw()
      if f != '':
         self.engine.loadRobot(f)
         self.redraw()

   def loadCamera(self):
      f = self.fileloaddialog("cameras","*.py")
      self.redraw()
      if f != '':
         self.engine.loadCamera(f)
         self.redraw()

   def freeRobot(self):
      self.engine.freeRobot()

   def INThandler(self, signum, frame):
      print "STOP ----------------------------------------------------"
      self.cleanup()

   def inform(self, message):
      try:
         self.status.set(message[0:50])
      except AttributeError: # gui not created yet
         print message

