from pyro.camera import *
from struct import unpack
import ImageDraw

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot, createVisionRep = 1):
      robot.startService('blob')
      self.robot = robot
      self.createVisionRep = createVisionRep
      self.blobdata = []
      self.blobimage = None
      self.depth = 3
      self.colorpos = { (255, 255, 255) : 0,
                        (255, 0, 0): 1,
                        (0, 255, 0) : 2, 
                        (0, 0, 255) : 3,
                        (0, 255, 255) : 4,
                        (255, 255, 0) : 5, 
                        (255, 0, 255) : 6, 
                        (0, 0, 0) : 7}
      self.colorpal = [ (255, 255, 255), 
                        (255, 0, 0),
                        (0, 255, 0),
                        (0, 0, 255),
                        (0, 255, 255),
                        (255, 255, 0),
                        (255, 0, 255),
                        (0, 0, 0) ]
      # do this last:
      Camera.__init__(self, 0, 0)
      
   def _update(self):
      """
      blobdata has list of blobs from device, listed by channel
      blobimage has a PIL image formed from bloblist
      """
      self.blobdata = self.robot.getServiceData('blob')
      if len(self.blobdata[0]) == 2: 
         self.width, self.height = self.blobdata[0]
         # mode, (x, y), color (r, g, b): 0 - 255
         # 'P' is an 8 bit index position:
         self.blobimage = PIL.PpmImagePlugin.Image.new('P', (self.width, self.height), 0)
         self.blobimage.putpalette([
            255, 255, 255, # background
            255, 0, 0,   # red
            0, 255, 0,   # green
            0, 0, 255,   # blue
            0, 255, 255, # yellow
            255, 255, 0,   # red
            255, 0, 255,   # red
            0, 0, 0,   # red
            ])
         draw = ImageDraw.ImageDraw(self.blobimage)
         for i in range(32): # each color channel
            for blobcount in range(len(self.blobdata[1][i])): # for each blob
               packedcolor, area, center_x, center_y, \
                            left, right, top, bottom, \
                            dist = self.blobdata[1][i][blobcount]
               r = packedcolor >> 16
               g = packedcolor >> 8 & 0x0000FF
               b = packedcolor & 0x0000FF
               color = self.colorpos[(r, g, b)]
               draw.setfill(color)
               draw.setink(color)
               # draw in the image area
               draw.rectangle((left, top, right, bottom))
         # turn into data for use in vision code
         if self.createVisionRep:
            # -------------------------------------------
            datastring = self.blobimage.tostring()
            self.data = [0] * self.width * self.height * self.depth
            for x in range(self.width * self.height):
               c = datastring[x]
               int_c = unpack('B', c)[0]
               r, g, b = self.colorpal[int_c]
               self.data[x * self.depth + 0] = r
               self.data[x * self.depth + 1] = g
               self.data[x * self.depth + 2] = b
            # -------------------------------------------
      else:
         self.blobimage = None

   def getImage(self):
      return self.blobimage
