#Define a Senses and drivers for Armor.  Currently,
#these are simply dummy values, but it's a start.

import pyro.robot.driver as driver
import pyro.gui.console as console
import math
import time

class ArmorSenseDriver(driver.Driver):
   #Sensor Accessor functions, currently all returning
   #dummy values

   def isStall(self):
      return 0

   def getTh(self, x):
      return 0

   def getThr(self, x):
      return 0

   def getTouchCount(self):
      return self.lld.getSenseCount('touch')

   def getTouchValue(self, sc, pos):
      return self.lld.getSense('touch', pos)

   def getRotCount(self):
      return self.lld.getSenseCount('rot')

   def getRotValue(self, sc, pos):
      return self.lld.getSense('rot', pos)
   
   def __init__(self, lld):
      """
      lld is the lowlevel driver associated with the electronics of the robot.
      Currently its a simulator
      """
      driver.Driver.__init__(self)
      self.lld = lld
      #create an array of 6 dummy touch sensor values
      #(one for each finger and thumb)
      self.touchArray = []
      for i in range(6):
         self.touchArray.append(i/6.0)

      #create a similar array of 10 rotation sensor values
      #(Because I thought there were 16 sensors total)
      self.rotArray = []
      for i in range(0, 10):
         self.rotArray.append(i/10.0)
      
      self.senses['robot'] = {}

      #robot senses, all funcs returning dummy values
      self.senses['robot']['stall'] = self.isStall

      #Since Armor is immobile, these will always be 0
      self.senses['robot']['x'] = lambda self, x: 0
      self.senses['robot']['y'] = lambda self, x: 0
      self.senses['robot']['z'] = lambda self, x: 0

      #Someday we might put a sensor on to monitor Armor's
      #torso rotation
      self.senses['robot']['th'] = self.getTh
      self.senses['robot']['thr'] = self.getThr

      self.senses['robot']['type'] = lambda self: 'Armor'
      self.senses['robot']['name'] = lambda self: 'Armor-1'

      #Define the robot's touch sensors, located in the
      #fingertips
      self.senses['touch'] = {}
      self.senses['touch']['count'] = self.getTouchCount
      self.senses['touch']['value'] = self.getTouchValue
      #is this right?
      self.senses['touch']['type'] = lambda self: 'scalar'

      self.senses['rotation'] = {}
      self.senses['rotation']['count'] = self.getRotCount
      self.senses['rotation']['value'] = self.getRotValue
      self.senses['rotation']['type'] = lambda self: 'scalar'

      console.log(console.INFO, 'Armor sense drivers loaded')

class ArmorControlDriver(driver.Driver):
   """
   In order to integrate this driver with the existing architecture, I'm going
   to give each motor its own control (Lshoulder rotate, Rshoulder pronate, etc).
   However, I think it might make more sense to let self.controls[x] have subarrays
   (e.g., self.controls['rotate']['Rshoulder']), or something like that.
   """
   
   def move(self, sc, trans, rot):
      self.translate(sc, trans)
      self.rotate(sc, rot)

   def translate(self, sc, value):
      pass

   def rotate(self, sc, value):
      pass

   def localize(self, sc, value):
      pass

   def update(self):
      #A hack to get the graphics to draw at a reasonable rate
      time.sleep(.1)

   def LShouldR(self, val):
      self.lld.incSenseByName('rot', 'LShoulder Rot', val)

   def LShouldP(self, val):
      self.lld.incSenseByName('rot', 'LShoulder Pron', val)

   def LElbowR(self, val):
      self.lld.incSenseByName('rot', 'LElbow Rot', val)

   def LElbowP(self, val):
      self.lld.incSenseByName('rot', 'LElbow Pron', val)

   def LWristR(self,val):
      self.lld.incSenseByName('rot', 'LWrist Rot', val)

   def LIndexF(self, val):
      pass

   def LIndexC(self, val):
      pass

   def LPinkyF(self, val):
      pass

   def LPinkyC(self, val):
      pass

   def LThumbF(self, val):
      pass

   def LThumbC(self, val):
      pass   
      
   def RShouldR(self, val):
      self.lld.incSenseByName('rot', 'RShoulder Rot', val)

   def RShouldP(self, val):
      self.lld.incSenseByName('rot', 'RShoulder Pron', val)

   def RElbowR(self, val):
      self.lld.incSenseByName('rot', 'RElbow Rot', val)

   def RElbowP(self, val):
      self.lld.incSenseByName('rot', 'RElbow Pron', val)

   def RWristR(self,val):
      self.lld.incSenseByName('rot', 'RWrist Rot', val)

   def RIndexF(self, val):
      pass

   def RIndexC(self, val):
      pass

   def RPinkyF(self, val):
      pass

   def RPinkyC(self, val):
      pass

   def RThumbF(self, val):
      pass

   def RThumbC(self, val):
      pass
   
   def __init__(self, lld):
      driver.Driver.__init__(self)
      self.lld = lld
      self.controls['move'] = self.move
      
      self.controls['LShoulder Rot']  = self.LShouldR
      self.controls['LShoulder Pron'] = self.LShouldP
      self.controls['LElbow Rot']     = self.LElbowR
      self.controls['LElbow Pron']    = self.LElbowP
      self.controls['LWrist Rot']     = self.LWristR
      self.controls['LIndex Flex']    = self.LIndexF
      self.controls['LIndex Curl']    = self.LIndexC
      self.controls['LPinky Flex']    = self.LPinkyF
      self.controls['LPinky Curl']    = self.LPinkyC
      self.controls['LThumb Flex']    = self.LThumbF
      self.controls['LThumb Curl']    = self.LThumbC

      self.controls['RShoulder Rot']  = self.RShouldR
      self.controls['RShoulder Pron'] = self.RShouldP
      self.controls['RElbow Rot']     = self.RElbowR
      self.controls['RElbow Pron']    = self.RElbowP
      self.controls['RWrist Rot']     = self.RWristR
      self.controls['RIndex Flex']    = self.RIndexF
      self.controls['RIndex Curl']    = self.RIndexC
      self.controls['RPinky Flex']    = self.RPinkyF
      self.controls['RPinky Curl']    = self.RPinkyC
      self.controls['RThumb Flex']    = self.RThumbF
      self.controls['RThumb Curl']    = self.RThumbC

      self.controls['update']         = self.update
      console.log(console.INFO, 'Armor control drivers loaded')

