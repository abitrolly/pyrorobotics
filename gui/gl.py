from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import Tkinter
import OpenGL.Tk as Opengl
from pyrobot.gui.drawable import *
from pyrobot.gui.renderer.gl import *
from pyrobot.gui.renderer.streams import *
from pyrobot.robot.service import Service
from time import time

# A GL gui

class GLView(Service): 
   def __init__(self, robot, width = 400, height = 400, db = 1, depth = 1):
      Service.__init__(self, serviceType = 'view')
      # This needs to be done here:
      self.robot = robot
      self.app = Tkinter.Tk()
      self.app.withdraw()
      # And other main windows should use Tkinter.Toplevel()
      self.width = width
      self.height = height
      self.genlist = 0
      self.lastRun = 0
      self.history = []
      self.history_pointer = 0
      self.lasttime = 0
      self.update_interval = 0.10
      self.db = db
      self.depth = depth
      self.win = None
      self.makeWindow()

   def makeWindow(self):
      self.visible = 1
      self.active = 1
      if self.win != None: return
      self.frame = Tkinter.Frame()
      self.frame.pack(side = 'top')
      self.win = Opengl.Opengl(master = self.frame, width = self.width, \
                               height = self.height, double = self.db, \
                               depth = self.depth)
      self.win.pack(side = 'top', expand = 1, fill = 'both')
      self.win.winfo_toplevel().title("3D Pyrobot Robot View")
      self.win.redraw = self.redraw
      self.mode = Tkinter.IntVar(self.win)
      self.mode.set(GL_EXP)
      self.init()

   def updateWindow(self):
      #current = time()
      #if current - self.lasttime >= self.update_interval:
      self.win.tkRedraw()
      #   self.lasttime = current
      #while self.win.tk.dooneevent(2): pass

   def fastUpdate(self):
      self.update_interval = 0.10

   def mediumUpdate(self):
      self.update_interval = 0.33

   def slowUpdate(self):
      self.update_interval = 1.0

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

   def redraw(self, win = 0):
      glClearColor(0.5, 0.5, 0.5, 0)
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      #glLoadIdentity()
      #self.resize(self.width, self.height)
      f = GenericStream()
      r = StreamRenderer(f)
      self.robot.draw({}, r) # get the draw commands
      f.close()
      s = StreamTranslator(f, GLRenderer()) # generate commands
      s.process() # draw the robot
      f.close()
      self.textView()
      self.bitmapString(1, self.height - 30, "X:", (0, 0, 0))
      self.bitmapString(1, self.height - 60, "Y:", (0, 0, 0))
      self.bitmapString(1, self.height - 90, "Th:", (0, 0, 0))
      if self.robot != 0:
         self.bitmapString(1, self.height - 30, "    %.2f" % self.robot.x, (1, 0, 0))
         self.bitmapString(1, self.height - 60, "    %.2f" % self.robot.y, (1, 0, 0))
         self.bitmapString(1, self.height - 90, "      %.2f" % self.robot.th, (1, 0, 0))
         if self.robot.stall:
            self.bitmapString(1, self.height - 120, "[BUMP!]", (1, 1, 0))
      else:
         self.bitmapString(1, self.height - 30, "    0.0", (1, 0, 0))
         self.bitmapString(1, self.height - 60, "    0.0", (1, 0, 0))
         self.bitmapString(1, self.height - 90, "      0.0", (1, 0, 0))

   def textView(self):
      glViewport(0,0,self.width,self.height)
      glMatrixMode(GL_PROJECTION)
      glLoadIdentity()
      glOrtho(0.0, self.width - 1.0, 0.0, self.height - 1.0, -1.0, 1.0)
      glMatrixMode(GL_MODELVIEW)
      glLoadIdentity()

   def bitmapString(self, x, y, str, color):
      glColor3fv(color)
      glRasterPos2f(x, y)
      for i  in range(len(str)):
         glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(str[i]))

if __name__ == '__main__':
   from pyrobot.plugins.robots.SimpleRobot import SimpleRobot

   class SimpleDrawableRobot(SimpleRobot):
      def _draw(self, options, renderer): # overloaded from robot
         #self.setLocation(self.senses['robot']['x'], \
         #                 self.senses['robot']['y'], \
         #                 self.senses['robot']['z'], \
         #                 self.senses['robot']['thr'] )
         renderer.xformPush()
         renderer.color((1, 0, 0))
        
         renderer.xformRotate(self.robot.th), (0, 0, 1))
         
         renderer.xformXlate(( 0, 0, .15))
         
         renderer.box((-.25, .25, 0), \
                      (.25, .25, 0), \
                      (.25, -.25, 0), \
                      (-.25, .25, .35)) # d is over a, CW
         
         renderer.color((1, 1, 0))
         
         renderer.box((.13, -.05, .35), \
                      (.13, .05, .35), \
                      (.25, .05, .35), \
                      (.13, -.05, .45)) # d is over a, CW
         
         renderer.color((.5, .5, .5))
         
         # wheel 1
         renderer.xformPush()
         renderer.xformXlate((.25, .3, 0))
         renderer.xformRotate(90, (1, 0, 0))
         renderer.torus(.06, .12, 12, 24)
         renderer.xformPop()
         
         # wheel 2
         renderer.xformPush()
         renderer.xformXlate((-.25, .3, 0))
         renderer.xformRotate(90, (1, 0, 0))
         renderer.torus(.06, .12, 12, 24)
         renderer.xformPop()
         
         # wheel 3
         renderer.xformPush()
         renderer.xformXlate((.25, -.3, 0))
         renderer.xformRotate(90, (1, 0, 0))
         renderer.torus(.06, .12, 12, 24)
         renderer.xformPop()
         
         # wheel 4
         renderer.xformPush()
         renderer.xformXlate((-.25, -.3, 0))
         renderer.xformRotate(90, (1, 0, 0))
         renderer.torus(.06, .12, 12, 24)
         renderer.xformPop()        
         
         # sonar
         #renderer.xformPush()
         #renderer.color((0, 0, .7))
         #for i in range(self.get('sonar', 'count')):
         #   y1, x1, z1 = -self.get('sonar', 'x', i), \
         #                -self.get('sonar', 'y', i), \
         #                self.get('sonar', 'z', i)
         #   #y2, x2, z2 = -self.get('sonar', 'ox', i), \
         #   #             -self.get('sonar', 'oy', i), \
         #   #             self.get('sonar', 'oz', i)
         #   # Those above values are off!
         #   # FIXME: what are the actual positions of sensor x,y?
         #   x2, y2, z2 = 0, 0, z1
         #   arc    = self.get('sonar', 'arc', i) # in radians
         #   renderer.ray((x1, y1, z1), (x2, y2, z2), arc)
         #   
         #renderer.xformPop()        
         # end of robot
         renderer.xformPop()

   robot = SimpleDrawableRobot()
   gui = GLView(robot)
   #gui.app.mainloop()
