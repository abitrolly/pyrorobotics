import Tkinter, time, sys
from pyro.gui import *
import pyro.gui.widgets.TKwidgets as TKwidgets
from pyro.system.version import *
from pyro.engine import *
import pyro.system as system
import pyro.system.share as share
from posixpath import exists
from pyro.tools.joystick import Joystick

def ask(title, qlist):
   d = TKwidgets.AskDialog(share.gui, title, qlist)
   ok = d.Show()
   if ok:
      retval = {"ok": 1}
      for (name, value) in qlist:
         retval[name] = d.textbox[name].get()
      d.DialogCleanup()
      return retval
   else:
      d.DialogCleanup()
      return {"ok" : 0}

if share.gui == 0:
   share.gui = Tkinter.Tk()
   share.gui.withdraw()
 
share.ask = ask

# A TK gui

class JoystickDriver(Joystick):
   def __init__(self, robot):
      self.robot = robot
      Joystick.__init__(self)
   def move(self, translate, rotate):
      self.robot.move(translate, rotate)

class AskDialog(TKwidgets.AlertDialog):
   def __init__(self, root, dict):
      TKwidgets.AlertDialog(self, root)
      self.dict = dict
   def SetupDialog(self):
      TKwidgets.AlertDialog.SetupDialog(self)
      self.bitmap['bitmap'] = 'warning'
      self.CreateButton("Yes", self.OkPressed)
      self.CreateButton("No", self.CancelPressed)

def ask(root, dict):
   box = AskDialog(root, dict)

class TKgui(Tkinter.Toplevel, gui): 
   def __init__(self, engine):
      Tkinter.Toplevel.__init__(self, share.gui)
      gui.__init__(self, 'TK gui', {}, engine)
      self.name = "<tkgui>" # for checking sys.stdout.name
      self.genlist = 0
      self.frame = Tkinter.Frame(self)
      self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                      fill = 'both')
      self.windowBrain = 0
      self.lastRun = 0
      self.lasttime = 0
      self.update_interval = 100
      self.update_interval_detail = 1.0
      self.lastButtonUpdate = 0
      self.maxBufferSize = 50000 # 50k characters in buffer
                                 #set to 0 for infinite
      #store the gui structure in something nice insted of python code

      menu = [('File',[['New brain...', self.newBrain],
                       None,
                       ['Editor',self.editor],
                       ['Variable Watcher', self.makeWatcher],
                       ['Exit',self.cleanup] 
                       ]),
              ('Window', [['Open all device windows', self.makeWindows],
                          None,
                          ['Fast Update 10/sec',self.fastUpdate],
                          ['Medium Update 3/sec',self.mediumUpdate],
                          ['Slow Update 1/sec',self.slowUpdate],
                          None,
                          ['Clear Messages', self.clearMessages],
                          ['Send Messages to Window', self.redirectToWindow],
                          ['Send Messages to Terminal', self.redirectToTerminal],
                          ]),
              ('Load',[['Server...', self.loadSim],
                       ['Robot...',self.loadRobot],
                       ['Brain...',self.loadBrain],
                       None,
                       ['Devices...',self.loadDevice],
                       #['Built-in Devices', None],
                       ]),
              ('Robot',[['Unload robot', self.freeRobot],
                        ['Unload brain', self.freeBrain],
                        None,
                        ['Connect robot', self.connectRobot],
                        ['Disconnect robot', self.disconnectRobot],
                        None,
                        ['Enable motors', self.enableMotors],
                        ['Disable motors', self.disableMotors],
                        None,
                        ['Joystick...', self.joystick],
                        ['Forward',self.stepForward],
                        ['Back',self.stepBack],
                        ['Left',self.stepLeft],
                        ['Right',self.stepRight],
                        None,
                        ['Stop Rotate',self.stopRotate],
                        ['Stop Translate',self.stopTranslate],
                        ['Stop All',self.stopEngine],
                        ['Update',self.update]
                        ]),
              ('Help',[['Help',self.help],
                       ['About',self.about],
                       ])
              ]
      
      button1 = [('Step',self.stepEngine),
                 ('Run',self.runEngine),
                 ('Stop',self.stopEngine),
                 ('Reload Brain',self.resetEngine),
                 ]

      # create menu
      self.mBar = Tkinter.Frame(self.frame, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)
      self.goButtons = {}
      self.menuButtons = {}
      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))

      #self.menuButtons["Built-in Devices"] = Tkinter.Menubutton(self.mBar,text="Test",underline=0)

      self.frame.winfo_toplevel().title("pyro@%s" % os.getenv('HOSTNAME'))
      self.frame.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.cleanup)

      # create a command text area:
      self.makeCommandArea()
      # Display:
      self.loadables = [ ('button', 'Server:', self.loadSim, self.editWorld, 0), # 0 = False
                         ('button', 'Robot:', self.loadRobot, self.editRobot, self.showAll),
                         ('button', 'Brain:', self.loadBrain, self.editBrain, self.openBrainWindow),
                        ]
      self.buttonArea = {}
      self.textArea = {}
      for item in self.loadables:
         self.makeRow(item)

      self.buttonArea["Robot:"]["state"] = 'normal'
      self.buttonArea["Server:"]["state"] = 'normal'
      ## ----------------------------------
      toolbar = Tkinter.Frame(self.frame)
      for b in button1:
         self.goButtons[b[0]] = Tkinter.Button(toolbar,text=b[0],command=b[1])
         self.goButtons[b[0]].pack(side=Tkinter.LEFT,padx=2,pady=2,fill=Tkinter.X, expand = "yes", anchor="n")
      toolbar.pack(side=Tkinter.TOP, anchor="n", fill='x', expand = "no")
      ## ----------------------------------
      self.makeRow(('status', 'Pose:', '', '', 0)) # 0 = False
      ## ----------------------------------
      self.textframe = Tkinter.Frame(self.frame)
      self.textframe.pack(side="top", expand = "yes", fill="both")
      # could get width from config
      self.status = Tkinter.Text(self.textframe, width = 60, height = 10,
                                 state='disabled',
                                 wrap='word',
                                 bg = "white")
      self.scrollbar = Tkinter.Scrollbar(self.textframe, command=self.status.yview)
      self.status.configure(yscroll=self.scrollbar.set)
      # for displaying fonts, colors, etc.: -------------------
      self.status.tag_config("red", foreground = "red")
      self.status.tag_config("black", foreground = "black")
      self.status.tag_config("green", foreground = "green")
      self.status.tag_config("blue", foreground = "blue")
      # --------------------------------------------------------
      self.scrollbar.pack(side="right", expand = "no", fill="y")
      self.status.pack(side="top", expand = "yes", fill="both")
      self.textframe.pack(side="top", fill="both")
      self.redirectToWindow()
      #self.tk_focusFollowsMouse()
      self.commandEntry.focus_force()
      self.inform("Pyro Version " + version() + ": Ready...")

   def showAll(self):
      if self.engine and self.engine.robot:
         print "=" * 30
         print self.engine.robot.getAll()

   def makeWindows(self):
      if self.engine and self.engine.robot:
         objs = self.engine.robot.getDevices()
         for serv in objs:
            self.engine.robot.getDevice(serv).makeWindow()
      else:
         print "Error: you need to load a robot first"

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
      self.commandEntry.bind('<Tab>', self.CommandTabKey)
      self.commandEntry.bind('<Control-p>', self.CommandPreviousKey)
      self.commandEntry.bind('<Control-n>', self.CommandNextKey)
      self.commandEntry.bind('<Up>', self.CommandPreviousKey)
      self.commandEntry.bind('<Down>', self.CommandNextKey)
      self.commandEntry["relief"] = "ridge"
      self.commandEntry.pack({'expand':'yes', 'side':'bottom', 'fill':'x'})
      self.commandFrame.pack({'expand':'no', 'side':'bottom', 'fill':'x'})
      # ---------------------------------      

   def makeRow(self, item):
      type, load, loadit, editit, viewit = item
      tempframe = Tkinter.Frame(self.frame)
      if type == 'button':
         self.buttonArea[load] = Tkinter.Button(tempframe, text = load,
                                                 width = 10, command = loadit,
                                                 state='disabled')
         self.textArea[load] = Tkinter.Button(tempframe, command=editit, justify="right", state='disabled')
         if viewit:
            self.buttonArea["View " + load] = Tkinter.Button(tempframe, text = "View",
                                                 width = 10, command = viewit,
                                                 state='disabled')
            self.buttonArea["View " + load].pack(side=Tkinter.RIGHT, fill = "none", expand = "no", anchor="n")
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

   def redrawWindowBrain(self):
      try:
         self.engine.brain.redraw()
         self.lastRun = self.engine.brain.lastRun
      except:
         pass
         
   def fastUpdate(self):
      self.update_interval = 100

   def mediumUpdate(self):
      self.update_interval = 333

   def slowUpdate(self):
      self.update_interval = 1000

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

   def CommandTabKey(self, event):
      from string import strip
      command = strip(self.commandEntry.get())
      if len(command) > 0:
         if command[-1] == ".":
            command = command[:-1]
      if self.engine.brain:
         self.environment["self"] = self.engine.brain
      else:
         self.environment["self"] = BrainStem(self.engine.robot)
      self.environment["engine"] = self.engine
      self.environment["robot"] = self.engine.robot
      self.environment["brain"] = self.engine.brain
      succeed = 0
      try:
         exec("_methods = %s/help\")" % command) in self.environment
         print "Help: ----------------------------------------------------"
         print self.environment["_methods"]
      except:
         pass
      try:
         if '"' in command:
            exec("_methods = %s\")" % command) in self.environment
            succeed = 1
         elif "'" in command:
            exec("_methods = %s\')" % command) in self.environment
            succeed = 1
      except:
         pass
      if succeed:
         prettyMethods = self.environment["_methods"]
         if (type(prettyMethods) != type([]) and
             type(prettyMethods) != type((1,))):
            prettyMethods = [prettyMethods]
      else:
         try:
            exec("_methods = dir(%s)" % command) in self.environment
            succeed = 1
         except:
            pass
         if succeed:
            methods = self.environment["_methods"]
            prettyMethods = [m for m in methods if m[0] != "_"]
         else:
            prettyMethods = ["Nothing appropriate"]
      cnt = 1
      print "Completion data: -----------------------------------------"
      for item in prettyMethods:
         try:
            print "%-20s " % item,
         except:
            print item
         if cnt % 3 == 0:
            print
         cnt += 1
      self.commandEntry.focus()
      if cnt % 3 != 1:
         print
      print "----------------------------------------------------------"
      return "break" # drops the tab from propagating

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

   def joystick(self):
      self.joywin = JoystickDriver(self.engine.robot)

   def about(self):
      self.redirectToTerminal()
      system.about()
      self.redirectToWindow()

   def help(self):
      self.redirectToTerminal()
      system.help()
      system.usage()
      self.redirectToWindow()

   def editor(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " &")
      else:
         os.system("emacs &")
   def newBrain(self):
      import os
      for i in range(1, 100):
         myfile = "~/MyBrain%d.py" % i
         if not exists(myfile):
            break
      os.system( "cp " + os.getenv("PYRO") + ("/build/brainTemplate.py %s" % myfile))
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " %s &" % myfile)
      else:
         os.system("emacs %s &"  % myfile)
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
   def generalUpdate(self):
      #
      # This contains the former contents of the while not self.done: loop in
      # .run()
      #
      now = time.time() 
      needToUpdateState = 1
      try: needToUpdateState = self.engine.brain.needToStop
      except: pass
      if needToUpdateState:
         #try:
         if type(self.engine.robot) != type(1):
            self.engine.robot.update()
         #except: pass
      self.redrawWindowBrain()
      if self.watcher:
         self.watcher.update(self.environment)
      # -----------------------
      if self.engine.robot != 0:
         if self.engine.robot.get('/robot/stall'):
            bump = "[STALL!]"
         else:
            bump = ''
         self.textArea['Pose:'].config(text = "X: %4.2f Y: %4.2f Th: %4.0f  %s"\
                                       % (self.engine.robot.get('robot', 'x'),
                                          self.engine.robot.get('robot', 'y'),
                                          self.engine.robot.get('robot', 'th'),
                                          bump))
         for device in self.engine.robot.getDevices():
            if self.engine.robot.getDevice(device).getVisible():
               self.engine.robot.getDevice(device).updateWindow()
      # Don't need to do the rest of this but once a second
      if now - self.lastButtonUpdate < 1:
         self.after(self.update_interval,self.generalUpdate)
         return
      self.lastButtonUpdate = now
      if self.textArea['Brain:']["text"] != self.engine.brainfile:
         self.textArea['Brain:'].config(text = self.engine.brainfile)
      if self.textArea['Server:']["text"] != self.engine.worldfile:
         self.textArea['Server:'].config(text = self.engine.worldfile)
      if self.textArea['Robot:']["text"] != self.engine.robotfile:
         self.textArea['Robot:'].config(text = self.engine.robotfile)
      # enable?
      if self.textArea["Brain:"]["text"]:
         if self.textArea["Brain:"]["state"] == 'disabled':
            self.textArea["Brain:"]["state"] = 'normal'
         if self.buttonArea['View Brain:']["state"] == 'disabled':
            self.buttonArea['View Brain:']["state"] = 'normal'
      else:
         if self.textArea["Brain:"]["state"] != 'disabled':
            self.textArea["Brain:"]["state"] = 'disabled'
         if self.buttonArea['View Brain:']["state"] != 'disabled':
            self.buttonArea['View Brain:']["state"] = 'disabled'
      if self.textArea["Server:"]["text"]:
         if self.textArea["Server:"]["state"] == 'disabled':
            self.textArea["Server:"]["state"] = 'normal'
      else:
         if self.textArea["Server:"]["state"] != 'disabled':
            self.textArea["Server:"]["state"] = 'disabled'
      if self.textArea["Robot:"]["text"]:
         if self.textArea["Robot:"]["state"] == 'disabled':
            self.textArea["Robot:"]["state"] = 'normal'
         if self.buttonArea['View Robot:']["state"] == 'disabled':
            self.buttonArea['View Robot:']["state"] = 'normal'
      else:
         if self.textArea["Robot:"]["state"] != 'disabled':
            self.textArea["Robot:"]["state"] = 'disabled'
         if self.buttonArea['View Robot:']["state"] != 'disabled':
            self.buttonArea['View Robot:']["state"] = 'disable'
      # Buttons?
      if self.textArea["Robot:"]["text"]: # have a robot!
         if self.menuButtons['Robot']["state"] == 'disabled':
            self.menuButtons['Robot']["state"] = 'normal'
         #if self.menuButtons['Load']["state"] == 'disabled':
         #   self.menuButtons['Load']["state"] = 'normal'
         if self.buttonArea["Brain:"]["state"] == 'disabled':
            self.buttonArea["Brain:"]["state"] = 'normal'
         if self.goButtons['Reload Brain']["state"] == 'disabled':
            self.goButtons['Reload Brain']["state"] = 'normal'
      else:
         if self.menuButtons['Robot']["state"] != 'disabled':
            self.menuButtons['Robot']["state"] = 'disabled'
         #if self.menuButtons['Load']["state"] != 'disabled':
         #   self.menuButtons['Load']["state"] = 'disabled'
         if self.buttonArea["Brain:"]["state"] != 'disabled':
            self.buttonArea["Brain:"]["state"] = 'disabled'
         if self.goButtons['Reload Brain']["state"] != 'disabled':
            self.goButtons['Reload Brain']["state"] = 'disabled'
      if self.textArea["Brain:"]["text"]:
         if self.goButtons['Run']["state"] == 'disabled':
            self.goButtons['Run']["state"] = 'normal'
         if self.goButtons['Step']["state"] == 'disabled':
            self.goButtons['Step']["state"] = 'normal'
         if self.goButtons['Stop']["state"] == 'disabled':
            self.goButtons['Stop']["state"] = 'normal'
         if self.goButtons['Reload Brain']["state"] == 'disabled':
            self.goButtons['Reload Brain']["state"] = 'normal'
         #if self.goButtons['View']["state"] == 'disabled':
         #   self.goButtons['View']["state"] = 'normal'
      else:
         if self.goButtons['Run']["state"] != 'disabled':
            self.goButtons['Run']["state"] = 'disabled'
         if self.goButtons['Step']["state"] != 'disabled':
            self.goButtons['Step']["state"] = 'disabled'
         if self.goButtons['Stop']["state"] != 'disabled':
            self.goButtons['Stop']["state"] = 'disabled'
         if self.goButtons['Reload Brain']["state"] != 'disabled':
            self.goButtons['Reload Brain']["state"] = 'disabled'
         #if self.goButtons['View']["state"] != 'disabled':
         #   self.goButtons['View']["state"] = 'disabled'
      self.after(self.update_interval,self.generalUpdate)
      
   def run(self, command = []):
      self.done = 0
      while len(command) > 0:
         print command[0],
         retval = command[0]
         if retval:
            self.processCommand(retval)
         command = command[1:]
         
      #
      # get the general update going -jp
      #
      self.after(self.update_interval,self.generalUpdate)
      self.mainloop()

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
      d = TKwidgets.LoadFileDialog(self, "Load " + filetype, skel, \
                                   pyro.pyrodir() + "/plugins/" + filetype)
      try:
         retval = d.Show()
         if retval == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
         else:
            d.DialogCleanup()
            return ""
      except:
         print "failed!"
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
      self.write(message + "\n", echo = 1)

   def parsePrint(self, message, tag = None):
      if tag:
         self.status.insert('end', message, tag)
      else:
         if "\n" in message.strip():
            self.status.insert('end', message)
         elif len(message) > 3 and message[:3] == ">>>":
            # parse it and display it
            self.status.insert('end', message[:3]) # >>>
            self.status.insert('end', message[3:], "red")
         elif ":" in message:
            parts = message.split(":")
            self.status.insert('end', parts[0], "blue")
            for p in parts[1:]:
               self.status.insert('end', ":")
               self.status.insert('end', p)
         elif "=" in message:
            parts = message.split("=")
            self.status.insert('end', parts[0], "blue")
            for p in parts[1:]:
               self.status.insert('end', "=")
               self.status.insert('end', p)
         elif len(message) > 3 and message.strip()[:-3] == "...":
            self.status.insert('end', message, "green")
         elif len(message) > 1 and message.strip()[-1] == "!":
            self.status.insert('end', message, "red")
         else:
            self.status.insert('end', message)
      
   def write(self, item, echo = 0, tag = None):
      try:
         self.status.config(state='normal')
         self.parsePrint("%s" % item, tag)
         self.status.config(state='disabled')
         self.status.see('end')
         if self.maxBufferSize:
            text = self.status.get(1.0, 'end')
            lenText = len(text)
            if lenText > self.maxBufferSize:
               self.status.config(state='normal')
               self.status.delete(1.0, float(lenText - self.maxBufferSize))
               self.status.config(state='disabled')
               self.status.see('end')
      except:
         if echo: print item
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

   def makeWatcher(self):
      self.watcher = TKwidgets.Watcher(self)

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
      d = TKwidgets.SaveFileDialog(self, "Load " + filetype, skel,
                                   pyro.pyrodir() + "/plugins/" + filetype)
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
   root = Tkinter.Tk()
   engine = Engine()
   gui = TKgui(engine)
   gui.inform("Ready...")
