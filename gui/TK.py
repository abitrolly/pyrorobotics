import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk
from pyro.gui import *
import pyro.gui.widgets.TKwidgets as TKwidgets
from pyro.system.version import *
from pyro.engine import *
import pyro.system as system
from pyro.gui.drawable import *
from pyro.gui.renderer.tk import *
from pyro.gui.renderer.streams import *
from time import time, sleep
import sys

# A TK gui

class TKgui(gui): 
   def __init__(self, engine, db = 1, depth = 1): 
      gui.__init__(self, 'TK gui', {}, engine)
      # This needs to be done here:
      self.app = Tkinter.Tk()
      self.app.wm_state('withdrawn')
      # And other main windows should use Tkinter.Toplevel()
      self.genlist = 0
      self.win = Tkinter.Toplevel()
      self.frame = Tkinter.Frame(self.win)
      self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                      fill = 'both')
      self.windowBrain = 0
      self.lastRun = 0
      self.lasttime = 0
      self.update_interval = 0.10
      self.update_interval_detail = 1.0
   
      #store the gui structure in something nice insted of python code

      menu = [('File',[['Editor',self.editor],
                       ['Save Map...', self.saveMap],
                       ['Exit',self.cleanup] 
                       ]),
              ('Window', [['Fast Update 10/sec',self.fastUpdate],
                          ['Medium Update 3/sec',self.mediumUpdate],
                          ['Slow Update 1/sec',self.slowUpdate],
                          None,
                          ['Clear Messages', self.clearMessages],
                          ['Send Messages to Window', self.redirectToWindow],
                          ['Send Messages to Terminal', self.redirectToTerminal],
                          ]),
              ('Load',[['Map...',self.loadMap],
                       ['Service...',self.loadService],
                       ['View...',self.loadView]
                       ]),
              ('Robot',[['Connect robot', self.connectRobot],
                        ['Disconnect robot', self.disconnectRobot],
                        None,
                        ['Enable motors', self.enableMotors],
                        ['Disable motors', self.disableMotors],
                        None,
                        ['Forward',self.stepForward],
                        ['Back',self.stepBack],
                        ['Left',self.stepLeft],
                        ['Right',self.stepRight],
                        ['Stop Rotate',self.stopRotate],
                        ['Stop Translate',self.stopTranslate],
                        ['Stop All',self.stopEngine],
                        ['Update',self.update]
                        ]),
              ('Help',[['Help',self.help],
                       ['Usage',self.usage],
                       ['Info',self.info],
                       ['About',self.about],
                       ['Inspector', self.inspector]
                       ])
              ]
      
      button1 = [('Step',self.stepEngine),
                 ('Run',self.runEngine),
                 ('Stop',self.stopEngine),
                 ('Reload',self.resetEngine),
                 ('View', self.openBrainWindow)
                 ]

      # create menu
      self.mBar = Tkinter.Frame(self.frame, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)
      self.goButtons = {}
      self.menuButtons = {}
      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))

      self.frame.winfo_toplevel().title("pyro@%s" % os.getenv('HOSTNAME'))
      self.frame.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.cleanup)

      # create a command text area:
      self.makeCommandArea()
      # Display:
      self.loadables = [ ('button', 'Simulator:', self.loadSim, self.editWorld),
                         ('button', 'Robot:', self.loadRobot, self.editRobot),
                         ('button', 'Brain:', self.loadBrain, self.editBrain),
                        ]
      self.buttonArea = {}
      self.textArea = {}
      for item in self.loadables:
         self.makeRow(item)

      self.buttonArea["Robot:"]["state"] = 'normal'
      self.buttonArea["Simulator:"]["state"] = 'normal'
      ## ----------------------------------
      toolbar = Tkinter.Frame(self.frame)
      for b in button1:
         self.goButtons[b[0]] = Tkinter.Button(toolbar,text=b[0],command=b[1])
         self.goButtons[b[0]].pack(side=Tkinter.LEFT,padx=2,pady=2,fill=Tkinter.X, expand = "yes", anchor="n")
      toolbar.pack(side=Tkinter.TOP, anchor="n", fill='x', expand = "no")
      ## ----------------------------------
      self.makeRow(('status', 'Pose:', '', ''))
      ## ----------------------------------
      self.textframe = Tkinter.Frame(self.frame)
      self.textframe.pack(side="top", expand = "yes", fill="both")
      self.status = Tkinter.Text(self.textframe, width = 40, height = 10,
                                 state='disabled', wrap='word')
      self.scrollbar = Tkinter.Scrollbar(self.textframe, command=self.status.yview)
      self.status.configure(yscroll=self.scrollbar.set)
      
      self.scrollbar.pack(side="right", expand = "no", fill="y")
      self.status.pack(side="top", expand = "yes", fill="both")
      self.textframe.pack(side="top", fill="both")
      self.redirectToWindow()
      self.inform("Pyro Version " + version() + ": Ready...")

   def makeCommandArea(self):
      # ---------------------------------
      self.commandFrame = Tkinter.Frame(self.frame)
      self.commandFrame['relief'] = 'raised'
      self.commandFrame['bd']	 = '2'
      self.commandLabel = Tkinter.Label(self.commandFrame)
      self.commandLabel["text"] = "Command:"
      self.commandLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
      # create a command 
      self.commandEntry = Tkinter.Entry(self.commandFrame)
      self.commandEntry.bind('<Return>', self.CommandReturnKey)
      self.commandEntry.bind('<Control-p>', self.CommandPreviousKey)
      self.commandEntry.bind('<Control-n>', self.CommandNextKey)
      self.commandEntry.bind('<Up>', self.CommandPreviousKey)
      self.commandEntry.bind('<Down>', self.CommandNextKey)
      self.commandEntry["relief"] = "ridge"
      self.commandEntry.pack({'expand':'yes', 'side':'bottom', 'fill':'x'})
      self.commandFrame.pack({'expand':'no', 'side':'bottom', 'fill':'x'})
      # ---------------------------------      

   def makeRow(self, item):
      type, load, loadit, editit = item
      tempframe = Tkinter.Frame(self.frame)
      if type == 'button':
         self.buttonArea[load] = Tkinter.Button(tempframe, text = load,
                                                 width = 10, command = loadit,
                                                 state='disabled')
         self.textArea[load] = Tkinter.Button(tempframe, command=editit, justify="right", state='disabled')
      elif type == 'status':
         self.buttonArea[load] = Tkinter.Label(tempframe, width = 10, text = load )
         self.textArea[load] = Tkinter.Label(tempframe, justify="left")
      self.buttonArea[load].pack(side=Tkinter.LEFT, fill = "none", expand = "no", anchor="n")
      self.textArea[load].pack(side=Tkinter.RIGHT, fill="x", expand = "yes", anchor="n")
      tempframe.pack(side = "top", anchor = "s", fill = "x")

   def redirectToWindow(self):
      # --- save old sys.stdout, sys.stderr
      self.sysstdout = sys.stdout
      sys.stdout = self # has a write() method
      self.sysstderror = sys.stderr
      sys.stderr = self # has a write() method

   def redirectToTerminal(self):
      # --- save old sys.stdout, sys.stderr
      sys.stdout = self.sysstdout
      sys.stderr = self.sysstderror

   def openBrainWindow(self):
      try:
         self.brain.window.state()
      except:
         if self.engine and self.engine.brain:
            self.engine.brain.makeWindow()

   def redrawViews(self):
      for p in self.engine.view:
         try:
            p.redraw(()) # pass in any options
         except Tkinter.TclError:
            #Window's closed; remove the view from the redraw list
            print "Removing view"
            self.engine.view.remove(p)

   def redrawWindowBrain(self):
      try:
         self.engine.brain.redraw()
         self.lastRun = self.engine.brain.lastRun
      except:
         pass
         
   def fastUpdate(self):
      self.update_interval = 0.10

   def mediumUpdate(self):
      self.update_interval = 0.33

   def slowUpdate(self):
      self.update_interval = 1.0

   def update(self): # FIX: I don't think this does anything
      pass

   def temp(self):
      if self.engine != 0:
         if self.engine.robot != 0:
            self.engine.robot.update()

   def CommandPreviousKey(self, event):
      if self.history_pointer - 1 <= len(self.history) and self.history_pointer - 1 >= 0:
         self.history_pointer -= 1
         self.commandEntry.delete(0, 'end')
         self.commandEntry.insert(0, self.history[self.history_pointer])
      else:
         print 'No more commands!', chr(7)

   def CommandNextKey(self, event):
      self.commandEntry.delete(0, 'end')
      if self.history_pointer + 1 <= len(self.history) and self.history_pointer + 1 >= 0:
         self.history_pointer += 1
         if self.history_pointer <= len(self.history) - 1:
            self.commandEntry.insert(0, self.history[self.history_pointer])
      else:
         print 'No more commands!', chr(7)

   def CommandReturnKey(self, event):
      from string import strip
      command = strip(self.commandEntry.get())
      self.commandEntry.delete(0, 'end')
      self.addCommandHistory(command)
      done = self.processCommand(command)
      if done:
         self.cleanup()
      #self.commandEntry.insert(0, filter)
      #self.commandButton.flash()
      #self.UpdateListBoxes()

   def info(self):
      self.redirectToTerminal()
      print "-------------------------------------------------------------"
      print "Brain file:\t%s" % self.engine.brainfile
      print "Brain:\t\t%s" % self.engine.brain
      print "Robot:\t\t%s" % self.engine.robot
      print "Worldfile:\t\t%s" % self.engine.worldfile
      print "-------------------------------------------------------------"
      self.redirectToWindow()

   def help(self):
      self.redirectToTerminal()
      system.help()
      self.redirectToWindow()

   def usage(self):
      self.redirectToTerminal()
      system.usage()
      self.redirectToWindow()

   def about(self):
      self.redirectToTerminal()
      system.about()
      self.redirectToWindow()

   def editor(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " &")
      else:
         os.system("emacs &")
   def editBrain(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.brainfile + "&")
      else:
         os.system("emacs " + self.engine.brainfile + "&")
   def editWorld(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.worldfile + "&")
      else:
         os.system("emacs " + self.engine.worldfile + "&")
   def editRobot(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.robotfile + "&")
      else:
         os.system("emacs " + self.engine.robotfile + "&")         
   def run(self, command = []):
      self.done = 0
      while len(command) > 0:
         print command[0],
         retval = command[0]
         if retval:
            self.processCommand(retval)
         command = command[1:]
      while not self.done:
         needToUpdateState = 1
         try: needToUpdateState = self.engine.brain.needToStop
         except: pass
         if needToUpdateState:
            try:
               self.engine.robot.update()
            except: pass
         self.redrawWindowBrain()
         self.redrawViews()
         if self.textArea['Brain:']["text"] != self.engine.brainfile:
            self.textArea['Brain:'].config(text = self.engine.brainfile)
         if self.textArea['Simulator:']["text"] != self.engine.worldfile:
            self.textArea['Simulator:'].config(text = self.engine.worldfile)
         if self.textArea['Robot:']["text"] != self.engine.robotfile:
            self.textArea['Robot:'].config(text = self.engine.robotfile)
         # enable?
         if self.textArea["Brain:"]["text"]:
            if self.textArea["Brain:"]["state"] == 'disabled':
               self.textArea["Brain:"]["state"] = 'normal'
         else:
            if self.textArea["Brain:"]["state"] != 'disabled':
               self.textArea["Brain:"]["state"] = 'disabled'
         if self.textArea["Simulator:"]["text"]:
            if self.textArea["Simulator:"]["state"] == 'disabled':
               self.textArea["Simulator:"]["state"] = 'normal'
         else:
            if self.textArea["Simulator:"]["state"] != 'disabled':
               self.textArea["Simulator:"]["state"] = 'disabled'
         if self.textArea["Robot:"]["text"]:
            if self.textArea["Robot:"]["state"] == 'disabled':
               self.textArea["Robot:"]["state"] = 'normal'
         else:
            if self.textArea["Robot:"]["state"] != 'disabled':
               self.textArea["Robot:"]["state"] = 'disabled'
         # Buttons?
         if self.textArea["Robot:"]["text"]:
            if self.menuButtons['Robot']["state"] == 'disabled':
               self.menuButtons['Robot']["state"] = 'normal'
            if self.menuButtons['Load']["state"] == 'disabled':
               self.menuButtons['Load']["state"] = 'normal'
            if self.buttonArea["Brain:"]["state"] == 'disabled':
               self.buttonArea["Brain:"]["state"] = 'normal'
            if self.goButtons['Reload']["state"] == 'disabled':
               self.goButtons['Reload']["state"] = 'normal'
         else:
            if self.menuButtons['Robot']["state"] != 'disabled':
               self.menuButtons['Robot']["state"] = 'disabled'
            if self.menuButtons['Load']["state"] != 'disabled':
               self.menuButtons['Load']["state"] = 'disabled'
            if self.buttonArea["Brain:"]["state"] != 'disabled':
               self.buttonArea["Brain:"]["state"] = 'disabled'
            if self.goButtons['Reload']["state"] != 'disabled':
               self.goButtons['Reload']["state"] = 'disabled'
         if self.textArea["Brain:"]["text"]:
            if self.goButtons['Run']["state"] == 'disabled':
               self.goButtons['Run']["state"] = 'normal'
            if self.goButtons['Step']["state"] == 'disabled':
               self.goButtons['Step']["state"] = 'normal'
            if self.goButtons['Stop']["state"] == 'disabled':
               self.goButtons['Stop']["state"] = 'normal'
            if self.goButtons['Reload']["state"] == 'disabled':
               self.goButtons['Reload']["state"] = 'normal'
            if self.goButtons['View']["state"] == 'disabled':
               self.goButtons['View']["state"] = 'normal'
         else:
            if self.goButtons['Run']["state"] != 'disabled':
               self.goButtons['Run']["state"] = 'disabled'
            if self.goButtons['Step']["state"] != 'disabled':
               self.goButtons['Step']["state"] = 'disabled'
            if self.goButtons['Stop']["state"] != 'disabled':
               self.goButtons['Stop']["state"] = 'disabled'
            if self.goButtons['Reload']["state"] != 'disabled':
               self.goButtons['Reload']["state"] = 'disabled'
            if self.goButtons['View']["state"] != 'disabled':
               self.goButtons['View']["state"] = 'disabled'
         # -----------------------
         if self.engine.robot != 0:
            if self.engine.robot.get('self', 'stall'):
               bump = "[BUMP!]"
            else:
               bump = ''
            self.textArea['Pose:'].config(text = "X: %4.2f Y: %4.2f Th: %4.0f  %s"\
                                          % (self.engine.robot.get('robot', 'x'),
                                             self.engine.robot.get('robot', 'y'),
                                             self.engine.robot.get('robot', 'th'),
                                             bump))
            for service in self.engine.robot.getServices():
               if self.engine.robot.getService(service).visible:
                  self.engine.robot.getService(service).updateWindow()
         while self.win.tk.dooneevent(2): pass
         sleep(self.update_interval)

   def fileloaddialog(self, filetype, skel, startdir = ''):
      from string import replace
      import pyro
      from os import getcwd, getenv, chdir
      retval = ""
      cwd = getcwd()
      if startdir == '':
         chdir(pyro.pyrodir() + "/plugins/" + filetype)
      else:
         chdir(startdir)
      d = TKwidgets.LoadFileDialog(self.win, "Load " + filetype, skel)
      try:
         if d.Show() == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
         else:
            d.DialogCleanup()
      except:
         # double-click bug. What should we do?
         doc = d.GetFileName()
         d.DialogCleanup()
         retval = doc
      chdir(cwd)
      return retval

   def refresh(self):
      #   self.win.autospin = 1
      #   self.win.xspin = 0
      #   self.win.yspin = 0
      #   self.win.after(500, self.win.do_AutoSpin)
      print "refresh!"

   def redraw_pass(self, win = 0): pass

   def redraw(self, win = 0):
      pass

   def inform(self, message):
      try:
         self.status.config(state='normal')
         self.status.insert('end', "%s\n" % (message))
         self.status.config(state='disabled')
         self.status.see('end')
      except AttributeError: # gui not created yet
         print message

   def make2DLPSWindow(self):
      pass

   def make3DLPSWindow(self):
      pass

   def makeGPSWindow(self):
      pass

   def write(self, item):
      try:
         self.status.config(state='normal')
         self.status.insert('end', "%s" % (item))
         self.status.config(state='disabled')
         self.status.see('end')
      except:
         pass
   def flush(self):
      pass

   def makeMenu(self, bar, name, commands):
      """ Assumes self.menuButtons exists """
      menu = Tkinter.Menubutton(bar,text=name,underline=0)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         if cmd:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
         else:
            menu.filemenu.add_separator()
      menu['menu'] = menu.filemenu
      return menu

   def inspector(self):
      import pyro.gui.inspector as Inspector
      import pyro.system.share as share
      share.brain = self.engine.brain
      share.robot = self.engine.robot
      share.engine = self.engine
      inspector = Inspector.Inspector(('share.brain', 'share.robot', 'share.engine'))

   def clearMessages(self):
      self.status.config(state='normal')
      self.status.delete(1.0, 'end')
      self.status.config(state='disabled')
      self.status.see('end')

   def filesavedialog(self, filetype, skel, startdir = ''):
      from string import replace
      import pyro
      from os import getcwd, getenv, chdir
      retval = ""
      cwd = getcwd()
      if startdir == '':
         chdir(pyro.pyrodir() + "/plugins/" + filetype)
      else:
         chdir(startdir)
      d = TKwidgets.SaveFileDialog(self.win, "Load " + filetype, skel)
      try:
         if d.Show() == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
         else:
            d.DialogCleanup()
      except:
         # double-click bug. What should we do?
         doc = d.GetFileName()
         d.DialogCleanup()
         retval = doc
      chdir(cwd)
      return retval

   def disconnectRobot(self):
      if self.engine.robot != 0:
         self.engine.robot.disconnect()
      else:
         raise ValueError, "select robot first"         

   def connectRobot(self):
      if self.engine.robot != 0:
         self.engine.robot.connect()
      else:
         raise ValueError, "select robot first"

   def enableMotors(self):
      if self.engine.robot != 0:
         self.engine.robot.enableMotors()
      else:
         raise ValueError, "select robot first"         

   def disableMotors(self):
      if self.engine.robot != 0:
         self.engine.robot.disableMotors()
      else:
         raise ValueError, "select robot first"

if __name__ == '__main__':
   gui = TKgui(Engine())
   gui.inform("Ready...")
   gui.run()
   gui.cleanup()
