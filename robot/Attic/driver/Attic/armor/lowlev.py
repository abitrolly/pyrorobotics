from math import floor

class ArmorLowlevel:
   def __init__(self):
      self.touchArray = []
      for i in range(6):
         self.touchArray.append(0.0)

      self.rotArray = []
      for i in range(10):
         self.rotArray.append(0.0)

      self.rotNames = {"LShoulder Rot"  : 0, \
                       "LShoulder Pron" : 1, \
                       "LElbow Rot"     : 2, \
                       "LElbow Pron"    : 3, \
                       "LWrist Rot"     : 4, \
                       "RShoulder Rot"  : 5, \
                       "RShoulder Pron" : 6, \
                       "RElbow Rot"     : 7, \
                       "RElbow Pron"    : 8, \
                       "RWrist Rot"     : 9}
      
      self.touchNames = {"LIndex"  : 0, \
                         "LPinky"  : 1, \
                         "LThumb"  : 2, \
                         "RIndex"  : 3, \
                         "RPinky"  : 4, \
                         "RThumb"  : 5}
   def getSenseCount(self, type):
      if type == 'rot':
         return len(self.rotArray)
      elif type == 'touch':
         return len(self.touchArray)
      else:
         raise KeyError, type + " not a type of sensor for Armor."


   def getSense(self, type, n):
      if type == 'rot':
         return self.rotArray[n]
      elif type == 'touch':
         return self.touchArray[n]
      else:
         raise KeyError, type + " not a type of sensor for Armor."

   def getSenseByName(self, type, name):
      if type == 'rot':
         return self.rotArray[self.rotNames[name]]
      elif type == 'touch':
         return self.touchArray[self.touchNames[name]]
      else:
         raise KeyError, type + " not a type of sensor for Armor."


   def incSense(self, type, n, val):
      if type == 'rot':
         self.rotArray[n] += val
         if not (0 <= self.rotArray[n] < 1):
            self.rotArray[n] -= floor(self.rotArray[n])
      elif type == 'touch':
         self.touchArray[n] += val
      else:
         raise KeyError, type + " not a type of sensor for Armor."

   def incSenseByName(self, type, name, val):
      if type == 'rot':
         self.incSense(type, self.rotNames[name], val)
      elif type == 'touch':
         self.incSense(type, self.touchNames[name], val)
      else:
         raise KeyError, type + " not a type of sensor for Armor."
