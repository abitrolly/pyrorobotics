from Tkinter import *
from pyro.gui import *
from pyro.gui.widgets.TKwidgets import *
from pyro.system.version import *
from pyro.engine import *
import pyro.system as system
from pyro.gui.drawable import *
import os
import sys
import signal
import time
import pyro.system

# A TK gui

class TKgui(gui):
   def __init__(self, engine, width = 400, height = 400, db = 1, depth = 1):
      Drawable.__init__(self, 'TK gui',{})
      self.width = width
      self.height = height
      self.engine = engine
      self.win = Tk()
      #width = width, height = height, double = db, \
      #                  depth = depth)
      #self.win.redraw = self.redraw
      #self.win.pack(side = 'top', expand = 1, fill = 'both')
      self.mode = IntVar(self.win)

      self.prevsighandler = signal.signal(signal.SIGINT, self.INThandler)
      self.inform("Ready...")

      self.win.title("pyro@%s - %s" % (os.getenv('HOSTNAME'), version()))
      # create a menu
      menu = Menu(self.win)
      self.win.config(menu=menu)
      
      filemenu = Menu(menu)
      menu.add_cascade(label="File", menu=filemenu)
      #        filemenu.add_command(label="Load...", command=self.cleanup)
      #        filemenu.add_separator()
      filemenu.add_command(label="Exit", command=self.cleanup)
      
      simmenu = Menu(menu)
      menu.add_cascade(label="Simulators", menu=simmenu)
      simmenu.add_command(label="Pioneer", command=self.loadpioneer)
      simmenu.add_command(label="PyroSim", \
                          command=self.loadpyrosim)
      
      robotmenu = Menu(menu)
      menu.add_cascade(label="Robot", menu=robotmenu)
      robotmenu.add_command(label="Load...", command=self.loadrobot)
      robotmenu.add_command(label="Disconnect!", \
                            command=self.disconnectrobot)
      
      brainmenu = Menu(menu)
      menu.add_cascade(label="Brain", menu=brainmenu)
      brainmenu.add_command(label="Load...", command=self.loadbrain)
      brainmenu.add_command(label="Disconnect", command=self.disconnectbrain)
      
      helpmenu = Menu(menu)
      menu.add_cascade(label="Help", menu=helpmenu)
      helpmenu.add_command(label="About...", command=system.usage)
      
      # create a toolbar
      toolbar = Frame(self.win)
      
      b = Button(toolbar, text="step!", width=6, command=self.step)
      b.pack(side=LEFT, padx=2, pady=2)
      b = Button(toolbar, text="reset!", width=6, command=self.loadbrain)
      b.pack(side=LEFT, padx=2, pady=2)
      b = Button(toolbar, text="run!", width=6, command=self.threaded_run)
      b.pack(side=LEFT, padx=2, pady=2)
      b = Button(toolbar, text="stop!", width=6, command=self.toggle_status)
      b.pack(side=LEFT, padx=2, pady=2)
      
      toolbar.pack(side=TOP, fill=X)
      
      # create a canvas
      can = Canvas(self.win, width=self.width, height=self.height, \
                      background='white')
      can.pack()
      
      # create a status bar
      self.status = StatusBar(self.win)
      self.status.pack(side=BOTTOM, fill=X)

   def fileloaddialog(self, filetype, skel):
      from pyro.gui.widgets.TKwidgets import *
      from string import replace
      import pyro
      from os import getcwd, getenv, chdir
      retval = ""
      cwd = getcwd()
      chdir(pyro.pyrodir() + "/plugins/" + filetype)
      d = LoadFileDialog(self.win, "Load " + filetype, skel)
      if d.Show() == 1:
         doc = d.GetFileName()
         d.DialogCleanup()
         retval = doc
      else:
         d.DialogCleanup()
      chdir(cwd)
      return retval

#   def step(self):
#      if self.engine.brain and self.engine.brain.status != 1:
#         self.engine.brain.status = 1
#         self.inform("Stepping...")
#         self.engine.brain.step()
#         time.sleep(.5) # give it time to run
#         self.engine.robot.act('move', 0, 0)
#         self.engine.brain.status = 0
#         self.inform("Stepped")
#      else:
#         self.inform('Brain not yet defined or already running')

       
if __name__ == '__main__':
   from pyro.engine import Engine
   gui = TKgui(Engine())
   gui.inform("Ready...")
   gui.init()
   gui.win.mainloop()
   gui.cleanup()
