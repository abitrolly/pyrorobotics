from pyro.camera import *
from struct import pack

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

   def _update(self):
      self.blobdata = self.robot.getServiceData('blobfinder')

   def getImage(self):
      self.width, self.height = self.blobdata[0]
      # mode, (x, y), color (r, g, b): 0 - 255
      image = PIL.PpmImagePlugin.Image.new('RGB', (self.width, self.height),
                                           (255, 255, 255))
      for i in range(32): # each color channel
         if len(self.blobdata) == 9:
            area, thing1, center_x, center_y, \
                  left_x, left_y, right_x, right_y, dist = self.blobdata[1]
            # draw in the image area
      return image
