# Test Image and Blob class

class Image:
   def __init__(self, width, height, init_val = 0):
      self.width = width
      self.height = height
      self.data = [init_val] * height * width
      self.equivList = [0] * 2000
      for n in range(2000):
         self.equivList[n] = n

   def display(self):
      for h in range(self.height):
         for w in range(self.width):
            if self.data[w + h * self.width]:
               print self.equivList[self.data[w + h * self.width]],
            else:
               print '.',
         print ''
      print ''

   def set(self, x, y, val):
      self.data[x + y * self.width] = val

   def get(self, x, y):
      return self.data[x + y * self.width]

   def reset(self, vector):
      for v in range(len(vector)):
         self.data[v] = vector[v]

   def blobify(self):
      self.equivList = [0] * 2000
      for n in range(2000):
         self.equivList[n] = n

      blob = Image(self.width, self.height)
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
               #elif self.get(w - 1, h) == 0 and self.get(w, h - 1) == 0:
               #      # new blob!
               #      blob.set(w, h, count)
               #      count += 1
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
                  else: # left is off
                     # new blob!
                     blob.set(w, h, count)
                     count += 1
      blob.equivList = self.equivList[:]
      blob.display()

if __name__ == '__main__':
   image = Image(20, 15)
   image.reset([1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 
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
   image.display()
   image.blobify()
