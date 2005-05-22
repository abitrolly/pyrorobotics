from pyrobot.gui.canvas import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.Tk import *

# A basic GL widget with some defaults:

class GLcanvas(canvas):
  def __init__(self, width = 200, height = 200, db = 1, depth = 1):
    canvas.__init__(self, width, height)
    self.win = Opengl(width = width, height = height, double = db, depth = depth)
    self.win.redraw = self.redraw
    self.win.pack(side = 'top', expand = 1, fill = 'both')
    self.mode = IntVar(self.win)
    self.mode.set(GL_EXP)

  def init(self):
    glMaterialf(GL_FRONT, GL_AMBIENT, [0, 0, 0, 1.])
    glMaterialf(GL_FRONT, GL_DIFFUSE, [0.61424, 0.04136, 0.04136, 1.0])
    glMaterialf(GL_FRONT, GL_SPECULAR, [0.727811, 0.626959, 0.626959, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 0.6 * 128.0)
    lightgray = (0.75, 0.75, 0.75, 1.0)
    gray = (0.5, 0.5, 0.5, 1.0)
    darkgray = (0.25, 0.25, 0.25, 1.0)
    black = (0, 0, 0)

    glLightfv(GL_LIGHT0, GL_SPECULAR, lightgray);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, gray);
    glLightfv(GL_LIGHT0, GL_AMBIENT, black);

    glDisable(GL_DITHER)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glLightf(GL_LIGHT0, GL_POSITION, [0.0, 3.0, 3.0, 0.0])
    glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, [0.0])
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)

  
  def redraw(self, o):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

if __name__ == '__main__':
  # test it out with standard fog/torus example:
  class Fog (GLcanvas):
    def __init__(self, width, height):
      # init canvas
      GLcanvas.__init__(self, width, height)
      # add some other items
      r1 = Radiobutton(text='GL_LINEAR', anchor=W, variable=self.mode,
                       value=GL_LINEAR, command=self.selectFog)
      r1.pack(side = 'top', expand = 1, fill = 'both')
      r2 = Radiobutton(text='GL_EXP', anchor=W, variable=self.mode,
                       value=GL_EXP, command=self.selectFog)
      r2.pack(side = 'top', expand = 1, fill = 'both')

    def drawTorus(self, x, y, z):
      glPushMatrix();
      glTranslatef(x, y, z);
      glMaterialf(GL_FRONT, GL_AMBIENT, [0.1745, 0.01175, 0.01175, 1.0])
      glMaterialf(GL_FRONT, GL_DIFFUSE, [0.61424, 0.04136, 0.04136, 1.0])
      glMaterialf(GL_FRONT, GL_SPECULAR, [0.727811, 0.626959, 0.626959, 1.0])
      glMaterialf(GL_FRONT, GL_SHININESS, 0.6 * 128.0)
      glutSolidTorus(0.275, 0.85, 20, 20)
      glPopMatrix()

    def redraw(self, o):
      GLcanvas.redraw(self, o)
      self.drawTorus(-4.0, -0.5, -1.0)
      self.drawTorus(-2.0, -0.5, -2.0)
      self.drawTorus(0.0, -0.5, -3.0)
      self.drawTorus(2.0, -0.5, -4.0)
      self.drawTorus(4.0, -0.5, -5.0)

    def init(self):
      # call superclass method (I wish there was a way to force this):
      GLcanvas.init(self) 
      glEnable(GL_FOG)
      fogColor = [0.5, 0.5, 0.5, 1.0]
      glFogi(GL_FOG_MODE, GL_EXP)
      glFogf(GL_FOG_COLOR, fogColor)
      glFogf(GL_FOG_DENSITY, 0.35)
      glHint(GL_FOG_HINT, GL_DONT_CARE)
      glClearColor(0.5, 0.5, 0.5, 1.0)
      
    def selectFog(self):
      val = self.mode.get()
      if val == GL_LINEAR:
        glFogf(GL_FOG_START, 1.0)
        glFogf(GL_FOG_END, 5.0)
        glFogi(GL_FOG_MODE, val)  
      elif val == GL_EXP:
        glFogi(GL_FOG_MODE, val)
      self.win.tkRedraw()

  f = Fog(50, 50)
  f.win.redraw = f.redraw
  f.init()
  f.win.mainloop()
