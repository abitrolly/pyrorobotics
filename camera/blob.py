from pyro.camera import *
from struct import pack
import ImageDraw

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot):
      if not robot.hasService('blobfinder'):
         raise "Robot does not have service", 'blobfinder'
      self.robot = robot
      self.blobdata = []
      # do this last:
      Camera.__init__(self, 0, 0)
      self.colorpos = { (255, 255, 255) : 0,
                        (255, 0, 0): 1,
                        (0, 255, 0) : 2, 
                        (0, 0, 255) : 3,
                        (0, 255, 255) : 4,
                        (255, 255, 0) : 5, 
                        (255, 0, 255) : 6, 
                        (0, 0, 0) : 7}
      
   def _update(self):
      self.blobdata = self.robot.getServiceData('blobfinder')

   def getImage(self):
      self.width, self.height = self.blobdata[0]
      # mode, (x, y), color (r, g, b): 0 - 255
      image = PIL.PpmImagePlugin.Image.new('P', (self.width, self.height), 0)
      image.putpalette([
         255, 255, 255, # background
         255, 0, 0,   # red
         0, 255, 0,   # green
         0, 0, 255,   # blue
         0, 255, 255, # yellow
         255, 255, 0,   # red
         255, 0, 255,   # red
         0, 0, 0,   # red
         ])
      draw = ImageDraw.ImageDraw(image)
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
      return image
