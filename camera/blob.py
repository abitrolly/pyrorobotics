from pyro.camera import *
from struct import pack

class BlobCamera(Camera):
   """
   """
   def __init__(self):
      Camera.__init__(self, 0, 0) 

   def _update(self):
      pass
   
   def getImage(self):
      #c = ''
      #for x in range(len(self.data)):
      #   c += pack('h', self.data[x])[0]
      #return PIL.PpmImagePlugin.Image.fromstring('RGB',
      #                                           (self.width, self.height),c)
      return None

