# Androids Image Library
# Spring 2002

import struct
from pyro.system import file_exists

class Image:
   """
   A Basic Image class. 
   """
   def __init__(self, width, height, depth = 3, init_val = 0):
      """
      Constructor. Depth is bytes per pixel.
      """
      self.width = width
      self.height = height
      self.depth = depth
      self.data = [init_val] * height * width * depth

   def loadFromFile(self, filename):
      """
      Method to load image from file. Currently must be in PBM P6 Format
      (color binary).
      """
      fp = open(filename, "r")
      type = fp.readline() # P6
      (width, height) = fp.readline().split(' ')
      self.width = int(width)
      self.height = int(height)
      self.depth = 3
      self.data = [0] * self.height * self.width * self.depth
      irange = int(fp.readline())
      x = 0
      while (x < self.width * self.height):
         c = fp.read(1)
         r = float(struct.unpack('h', c + '\x00')[0]) / float(irange)
         c = fp.read(1)
         g = float(struct.unpack('h', c + '\x00')[0]) / float(irange)
         c = fp.read(1)
         b = float(struct.unpack('h', c + '\x00')[0]) / float(irange)
         self.data[x * self.depth + 0] = r
         self.data[x * self.depth + 1] = g
         self.data[x * self.depth + 2] = b
         x += 1

   def saveToFile(self, filename):
      """
      Method to save image to a file. Currently will save PBM P5/P6 Format.
      """
      fp = open(filename, "w")
      if self.depth == 3:
         fp.writelines("P6\n") # P6
      else:
         fp.writelines("P5\n") # P5
      fp.writelines("%d %d\n" % (self.width, self.height))
      fp.writelines("255\n")
      x = 0
      while (x < self.width * self.height):
         for i in range(self.depth):
            c = int(self.data[x * self.depth + i] * 255.0)
            r = struct.pack('h', c)[0]
            fp.writelines(r)
         x += 1

   def grayScale(self):
      """
      Method to convert depth 3 color into depth 1 grayscale
      """
      if self.depth == 1:
         return
      data = [0] * self.width * self.height
      for h in range(self.height):
         for w in range(self.width):
            r = self.data[(w + h * self.width) * self.depth + 0]
            g = self.data[(w + h * self.width) * self.depth + 1]
            b = self.data[(w + h * self.width) * self.depth + 2]
            data[w + h * self.width] = (r + g + b) / 3.0
      self.data = data
      self.depth = 1

   def display(self):
      """
      Display Image in ASCII Art.
      """
      if self.depth == 3:
         line = ''
         for h in range(self.height):
            for w in range(self.width):
               r = self.data[(w + h * self.width) * self.depth + 0]
               g = self.data[(w + h * self.width) * self.depth + 1]
               b = self.data[(w + h * self.width) * self.depth + 2]
               if int(((r + g + b) / 3 ) * 9):
                  line += "%d" % int(((r + g + b) / 3 ) * 9)
               else:
                  line += '.'
            print line; line = ''
         print line; line = ''
      else:
         line = ''
         for h in range(self.height):
            for w in range(self.width):
               r = self.data[(w + h * self.width) * self.depth + 0]
               if int(r * 9):
                  line += "%d" % int(r * 9)
               else:
                  line += '.'
            print line; line = ''
         print line; line = ''

   def set(self, x, y, val, offset = 0):
      """
      Method to set a pixel to a value. offset is r, g, b (0, 1, 2)
      """
      self.data[(x + y * self.width) * self.depth + offset] = val

   def get(self, x, y, offset = 0):
      """
      Get a pixel value. offset is r, g, b = 0, 1, 2.
      """
      return self.data[(x + y * self.width) * self.depth + offset]

   def reset(self, vector):
      """
      Reset an image to a vector.
      """
      for v in range(len(vector)):
         self.data[v] = vector[v]

class Camera(Image):
   """
   A Fake camera class. Simulates live vision. Call update() to get image.
   """
   def __init__(self):
      Image.__init__(self, 0, 0, 3, 0) # will get info from file
      self.count = 0

   def update(self):
      """
      Update method for getting next sequence in simulated video camera.
      This will loop when it gets to the end.
      """
      if not file_exists("snaps/som-%d.ppm" % self.count):
         self.count = 0
      self.loadFromFile("snaps/som-%d.ppm" % self.count)
      self.count += 1

class Bitmap(Image):
   """
   Bitmap class. Based on Image, but has methods for blobs, etc.
   """
   def __init__(self, width, height, init_val = 0):
      Image.__init__(self, width, height, 1, init_val) # 1 bit depth
      self.equivList = [0] * 2000
      for n in range(2000):
         self.equivList[n] = n

   def display(self):
      """
      Display bitmap ASCII art.
      """
      for h in range(self.height):
         for w in range(self.width):
            if self.data[w + h * self.width]:
               print self.equivList[self.data[w + h * self.width]],
            else:
               print '.',
         print ''
      print ''

   def blobify(self):
      """
      Algorithm for 1 pass blobification. Returns a bitmap.
      Probably need to return a blob object.
      """
      self.equivList = [0] * 2000
      for n in range(2000):
         self.equivList[n] = n
      blob = Bitmap(self.width, self.height)
      count = 1
      for w in range(self.width):
         for h in range(self.height):
            if self.get(w, h):
               if h == 0 and w == 0: # if in upper left hand corner
                  # new blob!
                  blob.set(w, h, count)
                  count += 1
               elif w == 0:  # if in first col 
                  if self.get(w, h - 1): # if pixel above is on
                     # old blob
                     blob.set(w, h, blob.get(w, h - 1))
                  else: # above is off
                     # new blob!
                     blob.set(w, h, count)
                     count += 1
               elif h == 0:
                  if self.get(w - 1, h): # if pixel to left is on
                     # old blob
                     blob.set(w, h, blob.get(w - 1, h))
                  else: # left is off
                     # new blob!
                     blob.set(w, h, count)
                     count += 1
               elif self.get(w - 1, h)  and self.get(w, h - 1):
                  # both on!
                  if blob.get(w - 1, h) == blob.get(w, h - 1):
                     blob.set(w, h, blob.get(w - 1, h))
                  else: # intersection of two blobs
                     minBlobNum = min( self.equivList[blob.get(w - 1, h)],
                                       self.equivList[blob.get(w, h - 1)])
                     maxBlobNum = max( self.equivList[blob.get(w - 1, h)],
                                       self.equivList[blob.get(w, h - 1)])
                     blob.set(w, h, minBlobNum)
                     for n in range(2000):
                        if self.equivList[n] == maxBlobNum:
                           self.equivList[n] = minBlobNum
               else:
                  if self.get(w - 1, h): # if pixel to left is on
                     # old blob
                     blob.set(w, h, blob.get(w - 1, h))
                  elif self.get(w, h - 1): # if pixel above is on
                     # old blob
                     blob.set(w, h, blob.get(w, h - 1))
                  else: # left is off, above is off
                     # new blob!
                     blob.set(w, h, count)
                     count += 1
      blob.equivList = self.equivList[:]
      return blob

if __name__ == '__main__':
   # test 1
   bitmap = Bitmap(20, 15)
   bitmap.reset([1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 
                1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 
                1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
   bitmap.display()
   blob = bitmap.blobify()
   blob.display()
   # test 2
   image = Image(0, 0)
   image.loadFromFile("/usr/local/pyro/vision/snaps/som-1.ppm")
   image.saveToFile("test.ppm")
   image.grayScale()
   image.saveToFile("testgray.ppm")
   image.display()
   # test 3
   image = Camera()
   for x in range(10):
      image.update()
      image.display()
   print "All done! To see output, use xv to see test.ppm and testgray.ppm"
