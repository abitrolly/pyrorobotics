from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.Tk import *

from pyro.gui import *
from pyro.gui.widgets.TKwidgets import *
from pyro.system.version import *
from pyro.engine import *
import pyro.system as system
from pyro.gui.drawable import *
from pyro.gui.renderer.gl import *
from pyro.gui.renderer.streams import *

# A GL gui

class GLgui(gui):
   def __init__(self, engine, width = 400, height = 400, db = 1, depth = 1):
      gui.__init__(self, 'GL gui', {}, engine)

      self.width = width
      self.height = height
      self.genlist = 0
      self.frame = Frame()
      self.frame.pack(side = 'top')

      #store the gui structure in something nice insted of python code
      menu = [('file',[('exit',self.cleanup)]),
              ('simulators',[['load',self.loadSim]]),
              ('robot',[['load',self.loadRobot],
                        ['free',self.freeRobot]]),
              ('brain',[['load',self.loadBrain],
                        ['free',self.freeBrain]]),
              ('help',[['about',system.usage]])
              ]

      buttons = [('step',self.stepEngine),
                 ('reload',self.resetEngine),
                 ('refresh',self.refresh),
                 ('run',self.runEngine),
                 ('edit', self.editBrain),
                 ('stop',self.stopEngine),
                 ('F',self.stepForward),
                 ('B',self.stepBack),
                 ('L',self.stepLeft),
                 ('R',self.stepRight)]
      
      # create menu
      self.mBar = Frame(self.frame, relief=RAISED, borderwidth=2)
      self.mBar.pack(fill=X)

      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(entry[0],entry[1]))

      #make the buttons    
      toolbar = Frame(self.frame)
      toolbar.pack(side=TOP, fill=X)
      
      for b in buttons:
         Button(toolbar,text=b[0],width=6,command=b[1]).pack(side=LEFT,padx=2,pady=2)
         
      self.win = Opengl(master = self.frame, width = width,
                        height = height, double = db, depth = depth)

      self.win.pack(side = 'top', expand = 1, fill = 'both')
      #self.win.set_centerpoint(0, 0, 0)
      #self.frame.title("pyro@%s - %s" % (os.getenv('HOSTNAME'), version()))
      #self.wm_title("pyro@%s - %s" % (os.getenv('HOSTNAME'), version()))
      self.win.redraw = self.redraw

      self.mode = IntVar(self.win)
      self.mode.set(GL_EXP)

      # create a status bar
      self.status = StatusBar(self.frame)
      self.status.pack(side=BOTTOM, fill=X)
      self.inform("Pyro Version " + version() + ": Ready...")

   def editBrain(self):
      import os
      os.system("emacs " + self.engine.brainfile + "&")

   def makeMenu(self,name,commands):
      menu = Menubutton(self.mBar,text=name,underline=0)
      menu.pack(side=LEFT,padx="2m")
      menu.filemenu = Menu(menu)
      for cmd in commands:
         menu.filemenu.add_command(label=cmd[0],command=cmd[1])
      menu['menu'] = menu.filemenu
      return menu

   def run(self):
    self.win.mainloop()
    #while 1:
    #     self.redraw(self.win)
    #     self.win.tk.dooneevent()

   def init(self):
      # Do not specify a material property here.
      mat = [0.0, 0.0, 0.0, 1.0]
      glMaterialfv(GL_FRONT, GL_AMBIENT, mat)
      glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.61424, 0.04136, 0.04136, 1.0])
      glMaterialfv(GL_FRONT, GL_SPECULAR, [0.727811, 0.626959, 0.626959, 1.0])
      glMaterialfv(GL_FRONT, GL_SHININESS, 0.6 * 128.0)
      lightgray = [0.75, 0.75, 0.75, 1.0]
      gray = [0.5, 0.5, 0.5, 1.0]
      darkgray = [0.25, 0.25, 0.25, 1.0]
      black = [0, 0, 0]
      
      glLightfv(GL_LIGHT0, GL_SPECULAR, lightgray);
      glLightfv(GL_LIGHT0, GL_DIFFUSE, gray);
      glLightfv(GL_LIGHT0, GL_AMBIENT, black);
      
      glDisable(GL_DITHER)
      glEnable(GL_DEPTH_TEST)
      glDepthFunc(GL_LESS)
      glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 3.0, 3.0, 0.0])
      localview = [0.0]
      glLightModelfv(GL_LIGHT_MODEL_LOCAL_VIEWER, localview )
      glEnable(GL_CULL_FACE)
      glEnable(GL_LIGHTING)
      glEnable(GL_LIGHT0)
      glEnable(GL_COLOR_MATERIAL)
      glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
      #self.win.tkRedraw()

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

   def refresh(self):
      self.win.autospin = 1
      self.win.xspin = 0
      self.win.yspin = 0
      self.win.after(500, self.win.do_AutoSpin)

   def redraw(self, win = 0):
      glClearColor(0.5, 0.5, 0.5, 0)
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      f = GenericStream()
      r = StreamRenderer(f)
      self.draw({}, r)
      f.close()
      s = StreamTranslator(f, GLRenderer())
      s.process()
      f.close()
      if self.genlist == 0:
         self.win.update()
         self.win.autospin = 1
         self.win.xspin = 0
         self.win.yspin = 0
         self.win.after(500, self.win.do_AutoSpin)
         self.genlist = 1

if __name__ == '__main__':
   gui = GLgui()
   gui.inform("Ready...")
   gui.win.redraw = gui.redraw
   gui.init()
   gui.win.mainloop()
   gui.cleanup()
