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
      self.width = width
      self.height = height
      self.genlist = 0
      self.root = Tkinter.Tk()
      self.frame = Tkinter.Frame(self.root)
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
              ('Simulators',[['Load...',self.loadSim]]),
              ('Robot',[['Load...',self.loadRobot],
                        ['Unload',self.freeRobot]]),
              #['Load Camera...',self.loadCamera]]),
              ('Brain',[['Load...',self.loadBrain],
                        ['Unload',self.freeBrain],
                        ['Brain View', self.openBrainWindow]]),
              ('Plot',[['Load...',self.loadPlot]]),
              # ['robot', self.viewRobot]
              ('Move', [['Forward',self.stepForward],
                        ['Back',self.stepBack],
                        ['Left',self.stepLeft],
                        ['Right',self.stepRight],
                        ['Stop',self.stopEngine],
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
                 ('Reload',self.resetEngine),
                 ('Run',self.runEngine),
                 ('Edit', self.editBrain),
                 ('Stop',self.stopEngine)]

      # create menu
      self.mBar = Tkinter.Frame(self.frame, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)

      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(entry[0],entry[1]))

      # if show main buttons:
      if 1: # FIX: add a preference about showing buttons someday
         toolbar = Tkinter.Frame(self.frame)
         toolbar.pack(side=Tkinter.TOP, fill='both', expand = 1)
         for b in button1:
            Tkinter.Button(toolbar,text=b[0],width=6,command=b[1]).pack(side=Tkinter.LEFT,padx=2,pady=2,fill=Tkinter.X, expand = 1)

      self.frame.winfo_toplevel().title("pyro@%s" % os.getenv('HOSTNAME'))
      self.win = self.frame

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
      self.status = TKwidgets.StatusBar(self.frame)
      self.status.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
      self.inform("Pyro Version " + version() + ": Ready...")

   def openBrainWindow(self):
      try:
         self.windowBrain.state()
      except:
         self.windowBrain = Tkinter.Tk()
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
      print "-------------------------------------------------------------"

   def editBrain(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.brainfile + "&")
      else:
         os.system("emacs " + self.engine.brainfile + "&")
         
   def makeMenu(self,name,commands):
      menu = Tkinter.Menubutton(self.mBar,text=name,underline=0)
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         menu.filemenu.add_command(label=cmd[0],command=cmd[1])
      menu['menu'] = menu.filemenu
      return menu

   def run(self):
      if 1:
         self.done = 0
         while not self.done:
            needToUpdateState = 1
            try: needToUpdateState = self.engine.brain.needToStop
            except: pass
            if needToUpdateState:
               try: self.engine.robot.update()
               except: pass
            #try:
            self.redrawWindowBrain()
            try:
               self.engine.robot.camera.updateWindow()
            except:
               pass
            while self.win.tk.dooneevent(2): pass
            #except:
            #   print "Exiting main loop...", self.done
            #   self.done = 1
            sleep(self.update_interval)
         #self.win.mainloop()

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
