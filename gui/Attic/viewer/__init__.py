from PIL import ImageTk
from Tkinter import *
from math import *
from pyro.gui import drawable
import struct

class KheperaViewer(drawable.Drawable):
   """
   A class to view all the sensor data of the Khepera at once.
   """

   def __init__(self, imageSize):
      """
      Imagesize needs to be a (width, height) tuple, or None.  If it is None,
      we will assume that there is no camera attached.
      """
      self.imageSize = imageSize
      self.win = Tk()
      if not self.imageSize:
         self.radius = 25
      else:
         #inscribe the image in the circle representing the robot
         r = int(sqrt((imageSize[0]/2)**2 + (imageSize[1]/2)**2)) + 3
         if r < 25:
            self.radius = 25
         else:
            self.radius = r
         

      self.maxVals = {
         "ir" : 60.0/55.0, #going to assume that ir units are Robots for now
         "light" : 200.0,  #???
         "camera" : 255}
         

      self.canvas = Canvas(self.win, height = self.rad(7),
                           width = self.rad(7), bg = 'blue')
      
      self.circle = self.canvas.create_oval(self.rad(2.5),
                                            self.rad(2.5),
                                            self.rad(4.5),
                                            self.rad(4.5),
                                            fill = 'white',
                                            tags = 'circle')
      self.ir_circle = []
      ir_starts = [
         160.0, #0
         125.0, #1
         95.0,  #2
         75.0,  #3
         45.0,  #4
         10.0,  #5
         280.0, #6
         250.0] #7
      for i in range(8):
         self.ir_circle.append(self.canvas.create_arc(self.rad(2.5),
                                                      self.rad(2.5),
                                                      self.rad(4.5),
                                                      self.rad(4.5),
                                                      fill = 'red',
                                                      tags = 'ir',
                                                      start = ir_starts[i],
                                                      extent = 10.0))
      
      self.light_circle = []
      light_startextents = [
         (147.0, 33.0),
         (115.0, 32.0),
         (90.0, 25.0),
         (65.0, 25.0),
         (33.0, 32.0),
         (0.0, 33.0),
         (270.0, 35.0),
         (235.0, 35.0)]
      for i in range(8):
         arc = self.canvas.create_arc(self.rad(0.25),
                                      self.rad(0.25),
                                      self.rad(6.75),
                                      self.rad(6.75),
                                      fill = 'black',
                                      outline = '', #borderless
                                      tags = 'light',
                                      start = light_startextents[i][0],
                                      extent = light_startextents[i][1])
         self.light_circle.append(arc)

      if imageSize:
         print imageSize
         self.photo = ImageTk.PhotoImage("L", imageSize)
         print self.photo
         self.camera_view = self.canvas.create_image(self.rad(3.5),
                                                     self.rad(3.5),
                                                     tags = 'camera',
                                                     image=self.photo)

      self.motor_line = self.canvas.create_line(self.rad(5.75), self.rad(4.25),
                                                self.rad(5.75), self.rad(4.25),
                                                self.rad(5.75), self.rad(4.25),
                                                self.rad(5.75), self.rad(4.25),
                                                arrow = LAST,
                                                arrowshape = (7, 7, 3),
                                                width = 4,
                                                fill = 'white',
                                                tags = 'motor')
                                               
      self.canvas.tag_lower('circle', 'camera')
      self.canvas.tag_lower('ir', 'circle')
      self.canvas.tag_lower('light', 'ir')
      self.canvas.pack()


   def update(self, ir, light, motor, vision = None):
      """
      Update is expecting an 8-element IR vector scaled in ROBOTS, an
      8-elt light vector scaled in RAW (from 0 to 200), a 2-elt (trans., rot.)
      motor vector scaled from 0 to 1, and vision is an h*w-elt vector scaled
      from 0 to 255
      """
      for i in range(8):
         grayval = int((light[i]/self.maxVals['light']) * 100.0)
         self.canvas.itemconfigure(self.light_circle[i],
                                   fill='gray'+str(grayval))

      for i in range(8):
         percent = (ir[i]/self.maxVals['ir'])
         xy = self.scale(percent)
         self.canvas.coords(self.ir_circle[i], xy)

      if motor[1] == 0.5:
         self.canvas.coords(self.motor_line,
                            self.rad(5.75), self.rad(4.25 + 2*motor[0]),
                            self.rad(5.75), self.rad(4.25))
      else:
         self.canvas.coords(self.motor_line,
                            self.rad(5.75), self.rad(4.25 + 2*motor[0]),
                            self.rad(5.75), self.rad(4.25),
                            self.rad(5.75 + 2*(motor[1] - .5)), self.rad(4.25))

      if vision:
         graystr = ""
         for i in range(len(vision)):
            graystr += struct.pack("B", vision[i])
         
         img = ImageTk.Image.fromstring("L",
                                        (self.imageSize[0], self.imageSize[1]),
                                        graystr)
         self.photo.paste(img, None)

   def scale(self, percent):
      """
      Scale the bounding box of for the ir arcs
      """
      return (self.rad(2.5-2.0*percent),
              self.rad(2.5-2.0*percent),
              self.rad(4.5+2.0*percent),
              self.rad(4.5+2.0*percent))

   def rad(self, val):
      """
      Give an integer value for val * radius
      """
      return int(val * self.radius)
   
if __name__ == "__main__":
   print "Trying w/o vision:"
   kv = KheperaViewer(None)
   kv.update([.2, .4, .6, .8, 1.0, 1.03, .3, .5],
             [0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 199.0],
             [.3, 0])
   print "press RETURN..."
   raw_input()
   kv.update([.3, .9, .5, .8, .95, .8, .3, .7],
             [60.0, 20.0, 55.0, 75.0, 125.0, 135.0, 75.0, 5.0, 90.0],
             [.9, .75])
   raw_input()

   print "Testing w/vision:"
   kv = KheperaViewer((20, 10))
   a = [int(x*(200.0/255.0)) for x in range(200)]
   
   kv.update([.2, .4, .6, .8, 1.0, 1.03, .3, .5],
             [0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 199.0],
             [.3, 0],a)
   raw_input()
