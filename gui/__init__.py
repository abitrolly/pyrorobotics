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
      self.alreadyCleanedUp = 0
      self.engine = engine
      self.engine.gui = self
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
         self.inform("Running in thread...")
         self.engine.pleaseRun() # pass in callback, or not
         # self.engine.pleaseRun(self.redraw) # pass in callback
      elif retval == "runtillquit":
         self.done = 0
         self.engine.pleaseRun()
         while not self.done:
            pass
         return 1
      elif retval == "info":
         print "-------------------------------------------------------------"
         print "Brain file:\t%s" % self.engine.brainfile
         print "Brain:\t\t%s" % self.engine.brain
         print "Robot:\t\t%s" % self.engine.robot
         print "World:\t\t%s" % self.engine.worldfile
         print "-------------------------------------------------------------"
      elif retval == "help":
         help()
      elif retval == "usage":
         usage()
      elif retval == "update":
         if self.engine.robot != 0:
            self.engine.robot.update()
            self.inform("Done!")
         else:
            self.inform("Define a robot first!")
      elif retval == "about":
         about()
      elif retval == "reload":
         self.engine.reset()
      elif retval == "load robot":
         self.loadRobot()
      elif retval == "load brain":
         self.loadBrain()
      elif retval == "load simulator":
         print "Enter path (i.e., plugins/simulators/[Aria|Stage|Khepera])"
         self.loadSim(self.engine.worldfile)
      elif retval == "stop":
         self.engine.pleaseStop()
         self.inform("Stopped!")
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
            self.inform("Reloading...")
            self.engine.reset()
         else:
            self.inform("Need to load a brain first!")
      elif retval == "inspect":
         import pyro.gui.inspector as Inspector
         import pyro.system.share as share
         share.brain = self.engine.brain
         share.robot = self.engine.robot
         share.engine = self.engine
         inspector = Inspector.Inspector(('share.brain', 'share.robot', 'share.engine'))
      else:
         # elif len(retval) > 0 and retval[0] == "!":
         exp1 = """_retval = """ + string.strip(retval)
         _retval = "error"
         exp2 = string.strip(retval)
         brain = self.engine.brain
         robot = self.engine.robot
         engine = self.engine
         gui = self
         self = brain
         print ">>> ",
         print retval
         try:
            exec exp1
            print _retval
         except:
            try:
               exec exp2
               print "Ok"
            except:
               print gui.formatExceptionInfo()
         self = gui
      return 0

   def formatExceptionInfo(self, maxTBlevel=1):
      import sys, traceback
      cla, exc, trbk = sys.exc_info()
      excName = cla.__name__
      try:
         excArgs = exc.__dict__["args"]
      except KeyError:
         excArgs = ("<no args>",)
      excTb = traceback.format_tb(trbk, maxTBlevel)
      return "%s: %s %s" % (excName, excArgs[0], "in command line")

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
      """ Read a line from user """
      print "\nFilename: ",
      retval =  sys.stdin.readline()
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      return retval

   def cleanup(self):
      if not self.alreadyCleanedUp:
         self.alreadyCleanedUp = 1
         print "Cleaning up...",
         self.done = 1
         try:
            sys.stdout = self.sysstdout
            sys.stderr = self.sysstderr
         except:
            pass
         if self.engine != 0:
            self.engine.shutdown()
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
         self.freeBrain()
         self.engine.loadBrain(f)
         self.redraw()

   def loadMap(self):
      f = self.fileloaddialog("maps","*.py")
      self.redraw()
      if f != '':
         self.engine.loadMap(f)
         self.redraw()

   def loadView(self):
      f = self.fileloaddialog("views","*.py")
      self.redraw()
      if f != '':
         self.engine.loadView(f)
         self.redraw()

   def loadService(self):
      f = self.fileloaddialog("services","*.py")
      self.redraw()
      if f != '':
         if self.engine != 0 and self.engine.robot != 0:
            self.engine.robot.startService(f)
            self.redraw()

   def freeBrain(self):
      self.engine.pleaseStop()
      self.engine.destroyBrain()
      self.engine.freeBrain()
      self.engine.brainfile = ''

   def loadSim(self, worldfile = ''):
      pyropath = os.getenv('PYRO')
      f = self.fileloaddialog("simulators","*")
      self.redraw()
      if f != '':
         if worldfile == '':
            simulatorName = f.split('/')[-1]
            worldfile = self.fileloaddialog("worlds","*.world",
                                            "%s/plugins/worlds/%s/"
                                            % (pyropath, simulatorName))
         if worldfile != '':
            self.engine.worldfile = worldfile
            os.system(f + " " + worldfile + " &")
         self.redraw()
         
   def loadRobot(self):
      f = self.fileloaddialog("robots","*.py")
      self.redraw()
      if f != '':
         self.freeBrain()
         self.freeRobot()
         self.engine.loadRobot(f)
         self.redraw()

   def freeRobot(self):
      self.engine.pleaseStop()
      self.engine.freeRobot()
      self.engine.robotfile = ''

   def INThandler(self, signum, frame):
      print "STOP ----------------------------------------------------"
      self.engine.pleaseStop()
      self.cleanup()

   def inform(self, message):
      print message
      
   def filesavedialog(self, type, skel, startdir = ''):
      """ Read a line from user """
      print "\nFilename: ",
      retval =  sys.stdin.readline()
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      return retval

   def saveMap(self):
      f = self.filesavedialog("maps","*.py")
      if f != '':
         #save the map there
         pass

