class Renderer:
   """abstract interface for all things Renderable"""
   def __init__(self):
      raise "abstract method called in Renderer"
   def xformPush(self, dummy):
      raise "abstract method called in Renderer"
   def xformPop(self):
      raise "abstract method called in Renderer"
   def xformRotate(self,(qty,pt)):
      raise "abstract method called in Renderer"
   def xformXlate(self,(pt)):
      raise "abstract method called in Renderer"
   def xformScale(self,(scale)):
      raise "abstract method called in Renderer"
   def setLocation(self,x,y,z,theta):
      raise "abstract method called in Renderer"
   def color(self,(color)):
      raise "abstract method called in Renderer"
   def ray(self,(pta,ptb,arc)):
      raise "abstract method called in Renderer"
   def line(self,(pta,ptb)):
      raise "abstract method called in Renderer"
   def circle(self,(pt,norm,radius)):
      raise "abstract method called in Renderer"
   def triangle(self,(pta,ptb,ptc)):
      raise "abstract method called in Renderer"
   def text(self,(str)):
      raise "abstract method called in Renderer"
   def rectangle(self,(pta,ptb,ptc)):
      raise "abstract method called in Renderer"
   def box(self,(pta,ptb, ptc, ptd)):
      raise "abstract method called in Renderer"
   def torus(self, (ir, ora, n, r)):
      raise "abstract method called in Renderer"
   def polygon(self,*args):
      raise "abstract method called in Renderer"
   def clearState(self, dummy):
      raise "abstract method called int Render"
   def clearColor(self, color):
      raise "abstract method called int Render"



if __name__ == '__main__':

   from pyro.gui.canvas.GLcanvas import *
   import os
   FILEBASED = 1
   
   print 'Test... pickling:'
   print '  storing to file...'
   if FILEBASED:
      f = open("pickle.test", "w")
   else:
      f = GenericStream()

   s1 = StreamRenderer(f)
   s1.clearColor((.7,0.7,.7))
   s1.color((1, 0, 0))
   s1.triangle((0, 0, 0), (1, 0, 0), (0, 2, 0))
   #s1.text('hello world')
   s1.xformPush()
   s1.xformRotate(30, (1, 1, 1))
   s1.color((0, 1, 0))
   s1.triangle((0, 0, 0), (1, 0, 0), (0, 2, 0))
   s1.xformPop()
   s1.color((1, 1, 0))
   s1.polygon((.5, .5, 0), (0, 0, 0), (-.5, -.5, 0), (.25, -.25, 0))
   s1.color((0, 0, 1))
   s1.rectangle((-1, -2, -3), (-2, -3, -3), (0, -2, -3))
   s1.color((1, 0, 0))
   s1.box((0, 3, 3), (1, 2, 3), (2, 3, 3), (0, 3, 2)) # d is over a
   s1.xformXlate((-2, 0, 0))
   s1.xformScale(.5)
   s1.color((1, .5, 0))
   s1.xformRotate(45, (0, 0, 0))
   s1.torus(0.275, 0.85, 20, 20)
   ##s1.line((1, 2, 3), (4, 5, 6))
   ##s1.circle((1, 2, 3), 2, 4)
   f.close()
   
   print 'Test... unpickling with TTYRenderer:'
   if FILEBASED:
      print '  reading from file...'
      f = open("pickle.test", "r")
   else:
      print '  reading from string...'
      
   s2 = StreamTranslator(f, TTYRenderer(), debug = 0)
   s2.process()
   f.close()

   print 'Test... unpickling with GLRenderer:'
   class Test(GLcanvas):
      def redraw(self, o):
         global f
         GLcanvas.redraw(self, o)
         if FILEBASED:
            print '  reading from file...'
            f = open("pickle.test", "r")
         else:
            print '  reading from string...'
            f.reset()
         s2 = StreamTranslator(f, GLRenderer(), debug = 0)
         s2.process()
         f.close()

   win = Test(200, 200)
   win.o.redraw = win.redraw
   win.init()
   win.o.mainloop()

   if FILEBASED:
      os.remove("pickle.test")
      print "**** I deleted 'pickle.test'."

