import struct
from pyro.system import file_exists

class PyroImage:
   """
   A Basic Image class. 
   """
   def __init__(self, width = 0, height = 0, depth = 3, init_val = 0):
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
      self.data = self.getGrayScale()
      self.depth = 1

   def getGrayScale(self):
      """
      Method to convert depth 3 color into depth 1 grayscale
      """
      if self.depth == 1:
         return self.data
      data = [0] * self.width * self.height
      for h in range(self.height):
         for w in range(self.width):
            r = self.data[(w + h * self.width) * self.depth + 0]
            g = self.data[(w + h * self.width) * self.depth + 1]
            b = self.data[(w + h * self.width) * self.depth + 2]
            data[w + h * self.width] = (r + g + b) / 3.0
      return data

   def display(self):
      """
      Display PyroImage in ASCII Art.
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

   def setVal(self, x, y, val):
      """
      Method to set the entire RGB value of a pixel.
      val should be an n-tuple (or length n list), where n is the depth of the
      image.  For RGB, it should be of the form (r, g, b)
      """
      if len(val) != self.depth:
         print "Error in setVal: val is not the same length as depth"
         return
      
      for offset in range(self.depth):
         self.data[(x + y * self.width) * self.depth + offset] = val[offset]

   def incr(self, x, y, offset = 0):
      """
      Method to increment a pixel value. offset is r, g, b (0, 1, 2)
      """
      self.data[(x + y * self.width) * self.depth + offset] += 1


   def get(self, x, y, offset = 0):
      """
      Get a pixel value. offset is r, g, b = 0, 1, 2.
      """
      return self.data[(x + y * self.width) * self.depth + offset]

   def getVal(self, x, y):
      """
      Get the entire color value of the pixel in quetion, returned as a tuple.
      If this is an RGB image, it will be of the form (r, g, b).
      """
      start = (x + y * self.width) * self.depth
      end = start + self.depth
      return (tuple(self.data[start:end]))

   def reset(self, vector):
      """
      Reset an image to a vector.
      """
      for v in range(len(vector)):
         self.data[v] = vector[v]

   def filter(self, r, g, b, threshold):
      bitmap = Bitmap(self.width, self.height)
      for i in range( bitmap.width):
         for j in range( bitmap.height):
            redDiff = (self.get(i, j, 0) - r) ** 2
            greenDiff = (self.get(i, j, 1) - g) ** 2
            blueDiff = (self.get(i, j, 2) - b) ** 2
            finalval = 0
            if redDiff < threshold and \
               greenDiff < threshold and \
               blueDiff < threshold:
               finalval = 1
            bitmap.set(i, j, finalval, 0)
      return bitmap

   def histogram(self, cols = 20, rows = 20, initvals = 0):
      """
      Creates a histogram.
      """
      if not initvals:
         histogram = Histogram(cols, rows)
      else:
         histogram = initvals
      for h in range(self.height):
         for w in range(self.width):
            r = self.get(w, h, 0)
            g = self.get(w, h, 1)
            b = self.get(w, h, 2)
            if r == 0: r = 1.0
            br = min(int(b/float(r) * float(cols - 1)), cols - 1)
            gr = min(int(g/float(r) * float(rows - 1)), rows - 1)
            histogram.incr(br, gr)
      return histogram
   
class Histogram(PyroImage):
   """
   Histogram class. Based on Image, but has methods for display.
   """
   def __init__(self, width, height, init_val = 0):
      PyroImage.__init__(self, width, height, 1, init_val) # 1 bit depth

   def display(self):
      """
      Display bitmap ASCII art.
      """
      maxval = 0
      for h in range(self.height):
         for w in range(self.width):
            maxval = max(maxval, self.get(w, h))
      for h in range(self.height):
         for w in range(self.width):
            if maxval:
               print "%5d" % self.get(w, h),
            else:
               print ' ',
         print ''
      print ''

class Bitmap(PyroImage):
   """
   Bitmap class. Based on Image, but has methods for blobs, etc.
   """
   def __init__(self, width, height, init_val = 0):
      PyroImage.__init__(self, width, height, 1, init_val) # 1 bit depth
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
               try:
                  print self.equivList[self.data[w + h * self.width]],
               except:
                  print ">",
            else:
               print '.',
         print ''
      print ''

   def avgColor(self, img):
      """
      Return an n-tuple of the average color of the image where the bitmap is true,
      where n is the depth of img.  That is, using the bitmap as a mask, find the average color of img.
      img and self should have the same dimensions.
      """

      if not (self.width == img.width and self.height == img.height):
         print "Error in avgColor: Bitmap and Image do not have the same dimensions"
         return
      
      avg = []
      n = 0
      for i in range(img.depth):
         avg.append(0) #an n-array of zeros
         
      for x in range(self.width):
         for y in range(self.height):
            if (self.get(x, y)): #if the bitmap is on at this point
               for i in range(img.depth):
                  avg[i] += img.get(x, y, i)
                  n += 1

      if n == 0:
         return tuple(avg)
      else:
         for i in range(img.depth):
            avg[i] /= n
         return tuple(avg)
               
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

   def convolve(self, maskVector):
      mask = Bitmap(3, 3)
      mask.reset(maskVector)
      print self.width
      print self.height
      for w in range(self.width-2):
         for h in range(self.height-2):
            if self.get(w, h)== mask.get(0,0) and self.get(w, h+1)==mask.get(0,1)\
               and self.get(w, h+2)==mask.get(0,2) and self.get(w+1,h)==mask.get(1,0)\
               and self.get(w+2,h)==mask.get(2,0) and self.get(w+2,h+1)==mask.get(2,1)\
               and self.get(w+1,h+2)==mask.get(1,2) and self.get(w+2,h+2)==mask.get(2,2):
               self.set(w+1,h+1,mask.get(1, 1))

"""
assume that we are starting our x,y coordinates from the upper-left,
and starting at (0,0), such that (0,0) represents the upper-left-most
pixel
"""
class Point:
   def __init__(self, x=0, y=0):
      self.x = x
      self.y = y
   def set(self, x, y):
      self.x = x
      self.y = y
   def setx(self, x):
      self.x = x
   def sety(self, y):
      self.y = y
   def clear(self):
      self.x = 0
      self.y = 0

class Blob:
   def __init__(self, pixel):
      self.mass = 1
      self.ul = Point(pixel.x, pixel.y)
      self.lr = Point(pixel.x, pixel.y)
      self.cm = Point(pixel.x, pixel.y)
      self.next = 0

   def addpixel(self, pixel):
      if pixel.x < self.ul.x:
         self.ul.x = pixel.x
      elif pixel.x > self.lr.x:
         self.lr.x = pixel.x
      if pixel.y < self.ul.y:
         self.ul.y = pixel.y
      elif pixel.y > self.lr.y:
         self.lr.y = pixel.y
      self.cm.x = float(self.mass * self.cm.x + pixel.x)/float(self.mass + 1)
      self.cm.y = float(self.mass * self.cm.y + pixel.y)/float(self.mass + 1)
      self.mass += 1

   def joinblob(self, other):
      if other.ul.x < self.ul.x:
         self.ul.x = other.ul.x
      elif other.lr.x > self.lr.x:
         self.lr.x = other.lr.x
      if other.ul.y < self.ul.y:
         self.ul.y = other.ul.y
      elif other.lr.y > self.lr.y:
         self.lr.y = other.lr.y
      self.cm.x = float(self.mass * self.cm.x + other.mass * other.cm.x) \
                  /float(self.mass + other.mass)
      self.cm.y = float(self.mass * self.cm.y + other.mass * other.cm.y) \
                  /float(self.mass + other.mass)
      self.mass += other.mass   
         
   def width(self):
      return self.lr.x - self.ul.x + 1
   def height(self):
      return self.lr.y - self.ul.y + 1
   def area(self):
      return self.width() * self.height()
   def density(self):
      return float(self.mass)/float(self.area())
   def display(self):
      print "mass:", self.mass
      print "area:", self.area()
      print "density:", self.density()
      print "center of mass:", self.cm.x, ",", self.cm.y
      print "upper-left bound:", self.ul.x, ",", self.ul.y
      print "lower-right bound:", self.lr.x, ",", self.lr.y



class Blobdata:
   def __init__(self, bitmap):
      self.blobmap = Bitmap(bitmap.width, bitmap.height)
      self.bloblist = [0] * 2000
      count = 1

      # build the blobmap and construct unjoined Blob objects
      for w in range(bitmap.width):
         for h in range(bitmap.height):
            if bitmap.get(w, h):
               if h == 0 and w == 0: # in upper left corner -- new blob
                  self.bloblist[count] = Blob(Point(w,h))
                  self.blobmap.set(w, h, count)
                  count += 1
               elif w == 0:  # if in first col 
                  if bitmap.get(w, h - 1): # pixel above is on -- old blob
                     self.bloblist[self.blobmap.get(w,h-1)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w, h - 1))
                  else: # above is off -- new blob
                     self.bloblist[count] = Blob(Point(w,h))
                     self.blobmap.set(w, h, count)
                     count += 1
               elif h == 0: # in first row
                  if bitmap.get(w - 1, h): # pixel to left is on -- old blob
                     self.bloblist[self.blobmap.get(w-1,h)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w - 1, h))
                  else: # left is off -- new blob
                     self.bloblist[count] = Blob(Point(w,h))
                     self.blobmap.set(w, h, count)
                     count += 1
               elif bitmap.get(w - 1, h) and bitmap.get(w, h - 1): # both on
                  if self.blobmap.get(w - 1, h) == self.blobmap.get(w, h - 1):
                     self.bloblist[self.blobmap.get(w-1,h)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w - 1, h))
                  else: # intersection of two blobs
                     minBlobNum = min( \
                        self.blobmap.equivList[self.blobmap.get(w - 1, h)],
                        self.blobmap.equivList[self.blobmap.get(w, h - 1)])
                     maxBlobNum = max( \
                        self.blobmap.equivList[self.blobmap.get(w - 1, h)],
                        self.blobmap.equivList[self.blobmap.get(w, h - 1)])
                     self.bloblist[minBlobNum].addpixel(Point(w,h))
                     self.blobmap.set(w, h, minBlobNum)
                     for n in range(2000):
                        if self.blobmap.equivList[n] == maxBlobNum:
                           self.blobmap.equivList[n] = minBlobNum
               else:
                  if bitmap.get(w - 1, h): # left is on -- old blob
                     self.bloblist[self.blobmap.get(w-1,h)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w - 1, h))
                  elif bitmap.get(w, h - 1): # above is on -- old blob
                     self.bloblist[self.blobmap.get(w,h-1)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w, h - 1))
                  else: # left is off, above is off -- new blob
                     self.bloblist[count] = Blob(Point(w,h))
                     self.blobmap.set(w, h, count)
                     count += 1

      # count the number of blobs and join the actual blob objects
      self.nblobs = 0
      for n in range(1,count):
         if self.blobmap.equivList[n] == n:
            for m in range(n+1,count):
               if self.blobmap.equivList[m] == n:
                  self.bloblist[n].joinblob(self.bloblist[m])
                  self.bloblist[m] = 0
            self.nblobs += 1

      # shift the elements of bloblist[] so that the first Blob is at
      # bloblist[0] and the rest follow consecutively
      for n in range(1,count):
         m = n-1
         while self.bloblist[m] == 0:
            self.bloblist[m] = self.bloblist[m+1]
            self.bloblist[m+1] = 0
            if m == 0:
               break
            m -= 1


   # sort based on mass, area, or density
   def sort(self, mode="mass"):
      newlist = [0] * self.nblobs
      if mode == "mass":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               elif self.bloblist[n].mass > max:
                  max = self.bloblist[n].mass
                  m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist
      elif mode == "area":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               elif self.bloblist[n].area() > max:
                  max = self.bloblist[n].area()
                  m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist
      elif mode == "density":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               elif self.bloblist[n].density() > max:
                  max = self.bloblist[n].density()
                  m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist
      else:
         print "unknown sorting parameter:", mode

   def display(self):
      self.blobmap.display()
      print "Total number of blobs:", self.nblobs
      print ""
      for n in range(0,self.nblobs):
         print "Blob", n, ":"
         self.bloblist[n].display()            
         print ""

if __name__ == '__main__':
   from os import getenv
   import sys
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
   print "Do you want to run test 1: create bitmap, blobify, and display results? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      bitmap.display()
      blob = bitmap.blobify()
      blob.display()
      myblobdata = Blobdata(bitmap)
      myblobdata.sort("area")
      myblobdata.display()
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 2: create image from file, save it back out? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image = PyroImage(0, 0)
      image.loadFromFile(getenv('PYRO') + "/vision/snaps/som-1.ppm")
      image.saveToFile("test.ppm")
      print "Done! To see output, use 'xv test.ppm'"
   else:
      print "skipping..."
   print "Do you want to run test 3: create a grayscale image, save to file? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image.grayScale()
      image.saveToFile("testgray.ppm")
      #image.display()
      print "Done! To see output, use 'xv testgray.ppm'"
   else:
      print "skipping..."
   print "Do you want to run test 4: convert PyroImage to PIL image, and display it using xv? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      try:
         image.loadFromFile(getenv('PYRO') + "/vision/snaps/som-1.ppm")
         import PIL.PpmImagePlugin
         from struct import *
         c = ''
         for x in range(len(image.data)):
            c += pack('h', image.data[x] * 255.0)[0]
         i = PIL.PpmImagePlugin.Image.fromstring('RGB', (image.width, image.height),c)
         if getenv('DISPLAY'): i.show()
         print "Done!"
      except:
         print "Failed! Probably you don't have PIL installed"
   else:
      print "skipping..."
   print "Do you want to run test 5: convert Bitmap to PIL image, and display it using xv? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      try:
         import PIL.PpmImagePlugin
         from struct import *
         c = ''
         for x in range(len(bitmap.data)):
            c += pack('h', bitmap.data[x] * 255.0)[0]
         i = PIL.PpmImagePlugin.Image.fromstring('L', (bitmap.width, bitmap.height),c)
         if getenv('DISPLAY'): i.show()
         print "Done!"
      except:
         print "Failed! Probably you don't have PIL installed"
   else:
      print "skipping..."
   print "Do you want to run test 6: create a TK window, and display PPM from file or PyroImage? ",
   if getenv('DISPLAY') and sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      try:
         from Tkinter import *
         import Image, ImageTk
         class UI(Label):
            def __init__(self, master, im):
               if im.mode == "1":
                  # bitmap image
                  self.image = ImageTk.BitmapImage(im, foreground="white")
                  Label.__init__(self, master, image=self.image, bg="black", bd=0)
               else:
                  # photo image
                  self.image = ImageTk.PhotoImage(im)
                  Label.__init__(self, master, image=self.image, bd=0)
         root = Tk()
         filename = 'test.ppm'
         root.title(filename)
         #im = Image.open(filename)
         im = i
         UI(root, im).pack()
         root.mainloop()
         print "Done!"
      except:
         print "Failed! Probably you don't have Tkinter or ImageTk installed"
   else:
      print "skipping..."
   print "Do you want to run test 7: create a camera view, and display 10 frames in ASCII? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from pyro.camera.fake import FakeCamera
      image = FakeCamera()
      for x in range(10):
         image.update()
         image.display()
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 8: create a histogram of the image? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from pyro.camera.fake import FakeCamera
      image = FakeCamera()
      image.update()
      histogram = image.histogram(15, 20)
      histogram.display()
      #for x in range(99):
      #   image.update()
      #   histogram = image.histogram(15, 20, histogram)
      #   histogram.display()
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 9: create a filter bitmap of an image? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image = PyroImage()
      image.loadFromFile(getenv('PYRO') + '/vision/snaps/som-16.ppm')
      filter = image.filter(.65, .35, .22, .01) # r, g, b, threshold
      filter.saveToFile("filter.ppm")
      blob = filter.blobify()
      blob.display()
      print "Done! View filter bitmap with 'xv filter.ppm'"
   else:
      print "skipping..."
   print "Do you want to run test 10: find motion in 10 frames? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from pyro.camera.fake import FakeCamera
      camera = FakeCamera()
      camera.update()
      for x in range(10):
         camera.update(1)
         camera.motion.display()
         print "avg color of motion:", camera.motion.avgColor(camera)
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 11: find edges in bitmap ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      bitmap.display()
      mask = bitmap.convolve([1,1,1,
                              1,1,1,
                              1,1,1])
      print "Here is your final image"
      bitmap.display()
   else:
      print "skipping..."

   print "All done!"
