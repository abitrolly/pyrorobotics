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
   def __init__(self, engine, width = 400, height = 400, db = 1, depth = 1): 
      gui.__init__(self, 'TK gui', {}, engine)
      # This needs to be done here:
      self.app = Tkinter.Tk()
      self.app.wm_state('withdrawn')
      # And other main windows should use Tkinter.Toplevel()
      self.width = width
      self.height = height
      self.genlist = 0
      self.win = Tkinter.Toplevel()
      self.frame = Tkinter.Frame(self.win)
      self.frame.pack(side = 'top')
      self.windowBrain = 0
      self.lastRun = 0
      self.history = []
      self.history_pointer = 0
      self.lasttime = 0
      self.update_interval = 0.10
      self.update_interval_detail = 1.0
   
      #store the gui structure in something nice insted of python code

      menu = [('File',[['Editor',self.editor],
                       ['Exit',self.cleanup] 
                       ]),
              ('Move', [['Forward',self.stepForward],
                        ['Back',self.stepBack],
                        ['Left',self.stepLeft],
                        ['Right',self.stepRight],
                        ['Stop Rotate',self.stopRotate],
                        ['Stop Translate',self.stopTranslate],
                        ['Stop All',self.stopEngine],
                        ['Update',self.update]
                        ]),
              ('Refresh', [['Fast Update 10/sec',self.fastUpdate],
                           ['Medium Update 3/sec',self.mediumUpdate],
                           ['Slow Update 1/sec',self.slowUpdate]
                           ]),
              ('Load',[['Device...',self.loadDevice],
                       ['Service...',self.loadService],
                       ['Plot...',self.loadPlot]
                       ]),
              ('Help',[['Help',self.help],
                       ['Usage',self.usage],
                       ['Info',self.info],
                       ['About',self.about]
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
         self.mBar.tk_menuBar(self.makeMenu(entry[0],entry[1]))

      self.frame.winfo_toplevel().title("pyro@%s" % os.getenv('HOSTNAME'))
      self.frame.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.cleanup)

      self.commandFrame = Tkinter.Frame(self.frame)
      self.commandFrame['relief'] = 'raised'
      self.commandFrame['bd']	 = '2'
      self.commandFrame.pack({'expand':'no', 'side':'bottom', 'fill':'x'})

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
      self.commandEntry.pack({'expand':'yes', 'side':'right', 'fill':'x'})

      # create a status bar
      #self.status = TKwidgets.StatusBar(self.frame)
      #self.status.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

      self.textframe = Tkinter.Frame(self.frame)
      self.status = Tkinter.Text(self.textframe, height= 16,
                                 width = 60, state='disabled', wrap='word')
      self.scrollbar = Tkinter.Scrollbar(self.textframe, command=self.status.yview)
      self.status.configure(yscrollcommand=self.scrollbar.set)
      
      self.scrollbar.pack(side="right", fill="y")
      self.status.pack(side=Tkinter.LEFT, fill=Tkinter.X)
      self.textframe.pack(side = "bottom", fill = "x")

      # Display:
      self.loadables = [ ('button', 'Simulator:', self.loadSim, self.editWorld),
                         ('button', 'Robot:', self.loadRobot, self.editRobot),
#                         ('button', 'Camera:', self.loadCamera, self.editCamera),
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
      toolbar.pack(side=Tkinter.TOP, fill='both', expand = 1)
#      Tkinter.Label(toolbar, text="Brain:").pack(side="left")
      for b in button1:
         self.goButtons[b[0]] = Tkinter.Button(toolbar,text=b[0],width=6,command=b[1])
         self.goButtons[b[0]].pack(side=Tkinter.LEFT,padx=2,pady=2,fill=Tkinter.X, expand = 1)
      self.makeRow(('status', 'Pose:', '', ''))
      self.redirectToWindow()
      self.inform("Pyro Version " + version() + ": Ready...")

   def makeRow(self, item):
      type, load, loadit, editit = item
      tempframe = Tkinter.Frame(self.frame)
      if type == 'button':
         self.buttonArea[load] = Tkinter.Button(tempframe, text = load,
                                                 width=10, command = loadit,
                                                 state='disabled')
         self.textArea[load] = Tkinter.Button(tempframe, width=55,command=editit, justify="right", state='disabled')
      elif type == 'status':
         self.buttonArea[load] = Tkinter.Label(tempframe, width = 10, text = load )
         self.textArea[load] = Tkinter.Label(tempframe, width=55, justify="left")
      self.buttonArea[load].pack(side=Tkinter.LEFT)
      self.textArea[load].pack(side=Tkinter.RIGHT, fill="x")
      tempframe.pack(side = "top", anchor = "n", fill = "x")

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

   def redrawPlots(self):
      for p in self.engine.plot:
         try:
            p.redraw(()) # pass in any options
         except Tkinter.TclError:
            #Window's closed; remove the plot from the redraw list
            print "Removing plot"
            self.engine.plot.remove(p)

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

   def update(self):
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

   def addCommandHistory(self, command):
      if len(self.history) > 0:
         if command != self.history[ len(self.history) - 1]:
            self.history.append(command)
      else:
            self.history.append(command)
      self.history_pointer = len(self.history)
      
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
   def editCamera(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.camerafile + "&")
      else:
         os.system("emacs " + self.engine.camerafile + "&")
         
   def makeMenu(self,name,commands):
      menu = Tkinter.Menubutton(self.mBar,text=name,underline=0)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         menu.filemenu.add_command(label=cmd[0],command=cmd[1])
      menu['menu'] = menu.filemenu
      return menu

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
            try: self.engine.robot.update()
            except: pass
         self.redrawWindowBrain()
         self.redrawPlots()
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
            if self.menuButtons['Move']["state"] == 'disabled':
               self.menuButtons['Move']["state"] = 'normal'
            if self.menuButtons['Load']["state"] == 'disabled':
               self.menuButtons['Load']["state"] = 'normal'
            if self.buttonArea["Brain:"]["state"] == 'disabled':
               self.buttonArea["Brain:"]["state"] = 'normal'
            if self.goButtons['Reload']["state"] == 'disabled':
               self.goButtons['Reload']["state"] = 'normal'
         else:
            if self.menuButtons['Move']["state"] != 'disabled':
               self.menuButtons['Move']["state"] = 'disabled'
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
         try:
            self.engine.robot.camera.updateWindow()
         except:
            pass
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
      if d.Show() == 1:
         doc = d.GetFileName()
         d.DialogCleanup()
         retval = doc
      else:
         d.DialogCleanup()
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
         #self.status.set(message[0:50])
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
   
if __name__ == '__main__':
   gui = TKgui(Engine())
   gui.inform("Ready...")
   gui.run()
   gui.cleanup()
