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
      self.app.withdraw()
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

      menu = [('File',[['Edit Brain', self.editBrain],
                       ['Exit',self.cleanup] 
                       ]),
              ('Simulators',[['Load...', lambda x = self.engine.worldfile: self.loadSim(x)]]),
              ('Robot',[['Load...',self.loadRobot],
                        ['Unload',self.freeRobot],
                        ['Load Camera...',self.loadCamera]]),
              ('Brain',[['Load...',self.loadBrain],
                        ['Unload',self.freeBrain],
                        ['Brain View', self.openBrainWindow]]),
              ('Plot',[['Load...',self.loadPlot]]),
              # ['robot', self.viewRobot]
              ('Move', [['Forward',self.stepForward],
                        ['Back',self.stepBack],
                        ['Left',self.stepLeft],
                        ['Right',self.stepRight],
                        ['Stop Rotate',self.stopRotate],
                        ['Stop Translate',self.stopTranslate],
                        ['Stop All',self.stopEngine],
                        ['Update',self.update]
                        ]),
              ('View', [['Fast Update 10/sec',self.fastUpdate],
                        ['Medium Update 3/sec',self.mediumUpdate],
                        ['Slow Update 1/sec',self.slowUpdate]
                        ]),
              ('Help',[['Help',system.help],
                       ['Usage',system.usage],
                       ['Info',self.info],
                       ['About',system.about]
                       ])
              ]
      
      button1 = [('Step',self.stepEngine),
                 ('Run',self.runEngine),
                 ('Stop',self.stopEngine),
                 ('Reload',self.resetEngine),
]

      # create menu
      self.mBar = Tkinter.Frame(self.frame, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)

      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(entry[0],entry[1]))

      toolbar = Tkinter.Frame(self.frame)
      toolbar.pack(side=Tkinter.TOP, fill='both', expand = 1)
      Tkinter.Label(toolbar, text="Brain:").pack(side="left")
      self.goButtons = {}
      for b in button1:
         self.goButtons[b[0]] = Tkinter.Button(toolbar,text=b[0],width=6,command=b[1])
         self.goButtons[b[0]].pack(side=Tkinter.LEFT,padx=2,pady=2,fill=Tkinter.X, expand = 1)

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
      self.status = Tkinter.Text(self.textframe, height= 8,
                                 width = 60, state='disabled', wrap='word')
      self.scrollbar = Tkinter.Scrollbar(self.textframe, command=self.status.yview)
      self.status.configure(yscrollcommand=self.scrollbar.set)
      
      self.scrollbar.pack(side="right", fill="y")
      self.status.pack(side=Tkinter.LEFT, fill=Tkinter.X)
      self.textframe.pack(side = "bottom", fill = "x")

      # Display:
      self.loadables = [ ('button', 'Simulator:', self.loadSim, self.editWorld),
                         ('button', 'Robot:', self.loadRobot, self.editRobot),
                         ('button', 'Camera:', self.loadCamera, self.editCamera),
                         ('button', 'Brain:', self.loadBrain, self.editBrain),
                         ('status', 'Pose:', '', ''),
                        ]
      self.buttonArea = {}
      self.textArea = {}
      for item in self.loadables:
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
      self.buttonArea["Robot:"]["state"] = 'normal'
      self.buttonArea["Simulator:"]["state"] = 'normal'
      self.inform("Pyro Version " + version() + ": Ready...")

   def openBrainWindow(self):
      try:
         self.windowBrain.state()
      except:
         self.windowBrain = Tkinter.Toplevel()
         self.windowBrain.wm_title("pyro@%s: Brain View" % os.getenv('HOSTNAME'))
         self.canvasBrain = Tkinter.Canvas(self.windowBrain,width=550,height=300)
         self.canvasBrain.pack()

   def redrawWindowBrain(self):
      # FIX: behavior specific. How to put this in behavior code so
      # that each brain would know how to draw itself?
      try:
         self.windowBrain.state()
      except:
         return
      if self.engine and self.engine.brain and self.lastRun != self.engine.brain.lastRun:
         self.lastRun = self.engine.brain.lastRun
         self.canvasBrain.delete('pie')
         piecnt = 0
         for control in self.engine.brain.controls:
            piecnt += 1
            percentSoFar = 0
            piececnt = 0
            for d in self.engine.brain.pie:
               if control == d[0]:
                  piececnt += 1
                  portion = d[2]
                  try:
                     self.redrawPie(piecnt, percentSoFar, \
                                    piececnt, \
                                    "%s effects: %.2f" % (d[0], self.engine.brain.history[0][d[0]]),
                                    portion, \
                                    "(%.2f) %s IF %.2f THEN %.2f = %.2f" % (d[1], d[5], d[2],
                                                                            d[3], d[4]))
                  except:
                     pass
                  percentSoFar += portion
      else:
         try:
            self.canvasBrain.create_text(200,130, tags='pie',fill='black', text = "Ready...")
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

   def redrawPie(self, pie, percentSoFar, piececnt, controller,
                 percent, name):
      # FIX: behavior specific. How to put in Behavior-based code?
      xoffset = 5
      yoffset = 20
      width = 100
      row = (pie - 1) * (width * 1.5)
      colors = ['blue', 'red', 'tan', 'yellow', 'orange', 'black', 'azure', 'beige', 'brown', 'coral', 'gold', 'ivory', 'moccasin', 'navy', 'salmon', 'tan', 'ivory']
      self.canvasBrain.create_text(xoffset + 60,row + 10, tags='pie',fill='black', text = controller) 
      self.canvasBrain.create_arc(xoffset + 10,row + yoffset,width + xoffset + 10,row + width + yoffset,start = percentSoFar * 360.0, extent = percent * 360.0 - .001, tags='pie',fill=colors[(piececnt - 1) % 17])
      self.canvasBrain.create_text(xoffset + 300,row + 10 + piececnt * 20, tags='pie',fill=colors[(piececnt - 1) % 17], text = name)

   def info(self):
      print "-------------------------------------------------------------"
      print "Brain file:\t%s" % self.engine.brainfile
      print "Brain:\t\t%s" % self.engine.brain
      print "Robot:\t\t%s" % self.engine.robot
      print "Worldfile:\t\t%s" % self.engine.worldfile
      print "Camerafile:\t\t%s" % self.engine.camerafile
      print "-------------------------------------------------------------"

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
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         menu.filemenu.add_command(label=cmd[0],command=cmd[1])
      menu['menu'] = menu.filemenu
      return menu

   def run(self, command = []):
      if 1:
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
            if self.textArea['Brain:']["text"] != self.engine.brainfile:
               self.textArea['Brain:'].config(text = self.engine.brainfile)
            if self.textArea['Simulator:']["text"] != self.engine.worldfile:
               self.textArea['Simulator:'].config(text = self.engine.worldfile)
            if self.textArea['Robot:']["text"] != self.engine.robotfile:
               self.textArea['Robot:'].config(text = self.engine.robotfile)
            if self.textArea['Camera:']["text"] != self.engine.camerafile:
               self.textArea['Camera:'].config(text = self.engine.camerafile)
            # enable?
            if self.textArea["Brain:"]["text"]:
               self.textArea["Brain:"]["state"] = 'normal'
            else:
               self.textArea["Brain:"]["state"] = 'disable'
            if self.textArea["Simulator:"]["text"]:
               self.textArea["Simulator:"]["state"] = 'normal'
            else:
               self.textArea["Simulator:"]["state"] = 'disable'
            if self.textArea["Robot:"]["text"]:
               self.textArea["Robot:"]["state"] = 'normal'
            else:
               self.textArea["Robot:"]["state"] = 'disable'
            if self.textArea["Camera:"]["text"]:
               self.textArea["Camera:"]["state"] = 'normal'
            else:
               self.textArea["Camera:"]["state"] = 'disable'
            # Buttons?
            if self.textArea["Robot:"]["text"]:
               self.buttonArea["Camera:"]["state"] = 'normal'
               self.buttonArea["Brain:"]["state"] = 'normal'
               self.goButtons['Reload']["state"] = 'normal'
            else:
               self.buttonArea["Camera:"]["state"] = 'disable'
               self.buttonArea["Brain:"]["state"] = 'disable'
               self.goButtons['Reload']["state"] = 'disable'               
            if self.textArea["Brain:"]["text"]:
               self.goButtons['Run']["state"] = 'normal'
               self.goButtons['Step']["state"] = 'normal'
               self.goButtons['Stop']["state"] = 'normal'
            else:
               self.goButtons['Run']["state"] = 'disable'
               self.goButtons['Step']["state"] = 'disable'
               self.goButtons['Stop']["state"] = 'disable'               
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

   def fileloaddialog(self, filetype, skel):
      from string import replace
      import pyro
      from os import getcwd, getenv, chdir
      retval = ""
      cwd = getcwd()
      chdir(pyro.pyrodir() + "/plugins/" + filetype)
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
   
if __name__ == '__main__':
   gui = TKgui(Engine())
   gui.inform("Ready...")
   gui.run()
   gui.cleanup()
