import blob
from pyro.vision import *

class CBitmap:
    """
    Wrapper with constructor and destructor for blob.bitmap struct
    """
    def __init__(self, width, height):
        self.bitmap = blob.bitmap()
        blob.Bitmap_init(self.bitmap, width, height)

    def __del__(self):
        blob.Bitmap_del(self.bitmap)

    def set(self, x, y, data):
        """
        data must be able to be cast to an unsigned char (single byte)
        """
        blob.Bitmap_set(self.bitmap, x, y, data)

    def get(self, x, y):
        return blob.Bitmap_get(self.bitmap, x, y)
   
    def width(self):
        return self.bitmap.width

    def height(self):
        return self.bitmap.height
   
   
