import os
import sys
import signal
import time
import string
from pyro.gui.drawable import *
from pyro.gui.renderer.tty import *
from pyro.gui.renderer.streams import *
from pyro.system.version import version as version
from pyro.system import help as help

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
      
   def run(self):
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
         retval = sys.stdin.readline()
         print ""
         if retval == '':
            done = 1
            continue
         retval = retval.replace("\n", "")
         retval = retval.replace("\r", "")
         done = self.processCommand(retval)

   def processCommand(self, retval):
      if retval == "run":
         print "Running in thread..."
         self.engine.pleaseRun() # pass in callback, or not
         # self.engine.pleaseRun(self.redraw) # pass in callback
      elif retval == "help":
         help()
      elif retval == "reload":
         self.engine.reset()
      elif retval == "robot":
         self.loadRobot()
      elif retval == "brain":
         self.loadBrain()
      elif retval == "stop":
         self.engine.pleaseStop()
         print "Stopped!"
      elif retval == "quit" or retval == "exit" or retval == "bye":
         return 1
      elif retval[0] == "%":
         exp = string.strip(retval[1:])
         os.system(exp)
      elif retval == "edit":
         if self.engine.brainfile != '':
            os.system("emacs -nw " + self.engine.brainfile)
            print "Reloading..."
            self.engine.reset()
         else:
            print "Need to load a brain first"
      else:
         # elif len(retval) > 0 and retval[0] == "!":
         exp = string.strip(retval)
         brain = self.engine.brain
         robot = self.engine.robot
         try:
            exec exp
         except:
            print "Error in command: '" + exp + "'"
         #print "Unknown command: '" + retval + "'"
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

