# Fuzzy Logic Class
# D.S. Blank, 2001
# http://ai.uark.edu/

class Fuzzy:
   """
   Fuzzy logic class. Value is alwas between 0, and 1. Min, and Max
   can be any values.
   """
   def __init__(self, *args): # with no args, default to 0, 1, .5
      if len(args) == 0:
         self.Max = 1
         self.Min = 0
         self.Value = 0.5
      elif len(args) == 1: # with 1 arg, default to 0, 1, value
         self.Max = 1
         self.Min = 0
         self.SetUp(args[0])
      elif len(args) == 2: # with 2 args, default to min, max, .5
         self.Min = args[0]
         self.Max = args[1]
         self.Value = 0.5
      elif len(args) == 3: # with three args, default to min, max, value
         self.Min = args[0] # NOTE: this applies an Up() to value
         self.Max = args[1]
         self.SetUp(args[2])
   def __call__(self, *args):
      if len(args) == 0: # with no args, return value
         return self.Value
      elif len(args) == 1: # with 1 arg, return arg as value
         self.SetUp(args[0])
         return self.Value
      elif len(args) == 2: # with 2 args, default to min, max, .5
         raise "ERROR: what does this mean?"
      elif len(args) == 3: # with three args, default to min, max, value
         self.Min = args[0] # NOTE: this applies an Up() to value
         self.Max = args[1]
         self.SetUp(args[2])
         return self.Value
   def Up(self, value): # uphill, from left to right, slope
      temp = Fuzzy(self.Min, self.Max)
      temp.SetUp(value)
      return temp
   def Down(self, value): #downhill, from left to right, slope
      temp = Fuzzy(self.Min, self.Max)
      temp.SetDown(value)
      return temp
   def MinMax(self, value, min, max): # func
      if (value > max):
         return max
      elif (value < min):
         return min
      else:
         return value
   def Set(self, value): # set in range
      self.Value = float(self.MinMax(value, 0.0, 1.0))
      return self.Value
   def SetUp(self, value):
      if (self.Max == self.Min):
         self.Set(1.0)
      else:
         self.Set(float(value - self.Min)/(self.Max - self.Min))
      return self.Value
   def SetDown(self, value):
      if (self.Max == self.Min):
         self.Set(0.0)
      else:
         self.Set(1.0-(float(value - self.Min)/(self.Max-self.Min)))
      return self.Value

   def __str__(self):
      return "<Fuzzy instance value = " + str(self.Value) + \
             " min = " + str(self.Min) + \
             " max = " + str(self.Max) + ">"
   def __cmp__(self, other):
      if hasattr(other, 'Value'): # probably a Fuzzy
         return int(self.Value - other.Value)
      else:
         return (self.Value - other)

#      ret = Fuzzy(self.Min,self.Max)
#      if (self.Max - self.Min) == 0:
#         ret.Set(0)
#      else:
#         if (other > (self.Min + self.Max)/2.0):
#            ret.Set((other - self.Min) / (self.Min - self.Max))
#         else:
#            ret.Set(1.0-((other - self.Min) / (self.Min - self.Max)))
#      return ret
   
   def __add__ (self, other) :
      if hasattr(other, 'Value'): # could be Fuzzy on right
         return self.Value + other.Value
      else:
         return self.Value + other
   def __sub__ (self, other) :
      if hasattr(other, 'Value'): # could be Fuzzy on right
         return self.Value - other.Value
      else:
         return self.Value - other
   
   def __lshift__ (self, other) :
      return self.Down(other)
   
   def __rshift__ (self, other) :
      return self.Up(other)
   
   def __and__ (self, other) :
      ret = Fuzzy(self.Min, self.Max)
      if (self.Value < other.Value):
         ret.Set(self.Value)
      else:
         ret.Set(other.Value)
      return ret
   
   def __or__ (self, other):
      ret = Fuzzy(self.Min, self.Max)
      if (self.Value > other.Value):
         print "TEST1"
         ret.Set(self.Value)
      else:
         print "TEST2"
         ret.Set(other.Value)
      return ret

   def __neg__ (self) :
      return 1.0 - self.Value
   
   def __pos__ (self) :
      return self.Value
   
   def __abs__ (self) :
      return abs(self.Value)
   
   def __invert__ (self) :
      ret = Fuzzy(self.Min,self.Max)
      ret.Set(1.0 - self.Value)
      return ret

   def __float__(self) :
      return float(self.Value)

   def __nonzero__(self) :
      return (self.Value > 0.5)

   def __mul__ (self, other) :
      if hasattr(other, 'Value'): # could be Fuzzy on right
         return self.Value * other.Value
      else:
         return self.Value * other
   
   def __div__ (self, other) :
      if hasattr(other, 'Value'): # could be Fuzzy on right
         return self.Value / other.Value
      else:
         return self.Value / other

   __radd__ = __add__
   __rsub__ = __sub__

# Do we need these? What would they mean?
   
#   def __mod__ (self, other) :
#      return self.Value
   
#   def __divmod__ (self, other) :
#      return self.Value
   
#   def __pow__ (self, other, modulo = 0) :
#      return self.Value
   
#   def __xor__ (self, other) :
#      return self.Value
   
if __name__ == '__main__': # some tests
   x = Fuzzy(1, 7, 5)
   x2 = Fuzzy(1, 7, 2)
   y = Fuzzy(10, 100)
   z = Fuzzy(9, 4)
   f = Fuzzy(5, 10, 5)
   t = Fuzzy(11, 23, 23)

   print "1)", (z >> 8).Value
   print "2)", (z << 8).Value
   print "3)", x.Value
   print "4)", x2 + 0
   print "5)", not x
   print "6)", x & y
   print "7)", x or y
   print "8)", x == x2
   print "9)",
   if x and x2:
      print 'true'
   else:
      print 'false'
   print "10)", x - x2
   print "11)", x >> 5
   print "12)", Fuzzy(10, 1) >> 3

