import sys

class myframe:
   counter = 0
   def __init__(self, i, j):
      self.index = [i, j]
      self.id = myframe.counter
      myframe.counter += 1
      self.val = 1

   def getindex(self):
      return self.index

   def setval(self, val):
      self.val = val

   def getval(self):
      return self.val

class expander:
   def __init__(self, radius):
      self.radius = radius
      self.frame_list = {}
      self.pixel_list = []
      self.index_list = []
      self.pos = [0, 0]
      
      for i in range(0, radius * 2):
         self.pixel_list.append([])
         for j in range(0, radius * 2):
            self.pixel_list.append(0)

      map(self.addframe, [myframe(0,0), myframe(-1,0), \
                          myframe(-1,-1), myframe(0, -1)]) 

   def addframe(self, frm):
      (i, j) = (frm.getindex()[0], frm.getindex()[1])
      self.frame_list[(i, j)] = frm
      frm.setval(1) # activate
      
   def prompt(self):
      dir = raw_input("l, r, f, b, q, x, or [return]> ")
      shift = {}
      shift['horizontal'] = 0
      shift['vertical'] = 0
      
      if dir == 'l':
         shift['horizontal'] = -1
      elif dir == 'r':
         shift['horizontal'] =  1
      elif dir == 'f':
         shift['vertical'] = -1
      elif dir == 'b':
         shift['vertical'] =  1         
      elif dir == 'q':
         sys.exit(1)
      elif dir == 'x':
         #self.reset()
         pass
      else:
         pass

      self.expand(shift)
      
   def expand(self, shift):
      # need to add the case if two boundaries are reached
      # at the same time?

      dh = shift['horizontal']
      if dh != 0:
         if dh == 1:
            (i, j) = (self.pos[0] + 1, self.pos[1])
         elif dh == -1:
            (i, j) = (self.pos[0] - 2, self.pos[1])
         else:
            print "error"
            sys.exit(-1)
         
         # create or activate frames
         if not self.frame_list.has_key((i, j)):
            self.addframe(myframe(i, j))
         else:
            self.frame_list[i, j].setval(1) # activate
         if not self.frame_list.has_key((i, j - 1)):
            self.addframe(myframe(i, j - 1))
         else:            
            self.frame_list[i, j - 1].setval(1) # activate

         # swap out frames
         if self.frame_list.has_key((i - 2 * dh, j)):
            self.frame_list[i - 2 * dh, j].setval(2) # swap out
         if self.frame_list.has_key((i - 2 * dh, j - 1)):
            self.frame_list[i - 2 * dh, j - 1].setval(2) # swap out
         self.pos[0] += dh

      dv = shift['vertical']
      if dv != 0:
         if dv == 1:
            (i, j) = (self.pos[0], self.pos[1] + dv)
         if dv == -1:
            (i, j) = (self.pos[0], self.pos[1] + 2 * dv)

         # create or activate frames
         if not self.frame_list.has_key((i, j)):
            self.addframe(myframe(i, j)) 
         else:
            self.frame_list[i, j].setval(1) # activate
         if not self.frame_list.has_key((i - 1, j)):
            self.addframe(myframe(i - 1, j)) 
         else:
            self.frame_list[i - 1, j].setval(1) # activate

         # swap out frames
         if self.frame_list.has_key((i, j - 2 * dv)):
            self.frame_list[i, j - 2 * dv].setval(2) # swap out
         if self.frame_list.has_key((i - 1, j - 2 * dv)):
            self.frame_list[i - 1, j - 2 * dv].setval(2) # swap out
         self.pos[1] += dv

      print "(dh, dv, self.pos):", (dh, dv, self.pos)

   def update(self):
      for j in range(0, self.radius * 2):
         for i in range(0, self.radius * 2):
            ii = i - self.radius
            jj = j - self.radius
            if self.frame_list.has_key((ii, jj)):
               print self.frame_list[(ii, jj)].getval(),
            else:
               print 0,
         print ""
      print ""

if (__name__ == '__main__'):
   e = expander(10)

   while(1):
      e.update()
      e.prompt()
