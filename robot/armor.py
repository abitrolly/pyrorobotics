#Define ArmorRobot, an interface to the
#pair of arms

from pyro.robot import *
from pyro.robot.driver.armor import *
from pyro.robot.driver.armor.lowlev import *
import math

class ArmorRobot(Robot):
   def getValByName(self, name):
      return self.get(self.sensorNames[name][0], \
                      self.sensorNames[name][1], \
                      self.sensorNames[name][2])

   def u2deg(self, val):
      """
      Given a value between 0 and 1, convert it to a radian value
      between 0 and 360
      """
      return val*360
   
   def __init__(self, name = None, simiulator = 1):
      Robot.__init__(self, name, "Armor")
      self.dev = None
      Robot.load_drivers(self)
      self.sensorNames = {"LShoulder Rot"  : ['rotation', 'value', 0], \
                          "LShoulder Pron" : ['rotation', 'value', 1], \
                          "LElbow Rot"     : ['rotation', 'value', 2], \
                          "LElbow Pron"    : ['rotation', 'value', 3], \
                          "LWrist Rot"     : ['rotation', 'value', 4], \
                          "RShoulder Rot"  : ['rotation', 'value', 5], \
                          "RShoulder Pron" : ['rotation', 'value', 6], \
                          "RElbow Rot"     : ['rotation', 'value', 7], \
                          "RElbow Pron"    : ['rotation', 'value', 8], \
                          "RWrist Rot"     : ['rotation', 'value', 9], \
                          "LIndex"         : ['touch', 'value', 0], \
                          "LPinky"         : ['touch', 'value', 1], \
                          "LThumb"         : ['touch', 'value', 2], \
                          "RIndex"         : ['touch', 'value', 3], \
                          "RPinky"         : ['touch', 'value', 4], \
                          "RThumb"         : ['touch', 'value', 5]}

   def _draw(self, options, renderer):
      #Start Body
      renderer.xformPush()
      renderer.color((.5, .5, .5))
      renderer.xformXlate((0, 0, 3))
      renderer.xformRotate(self.get('robot', 'th'), (0, 0, 1))
      renderer.box((-.75, .5, -.25), \
                   (.75, .5, -.25), \
                   (.75, -.5, -.25), \
                   (-.75, .5, .25))

      #Start Left Upper Arm
      renderer.xformPush()
      renderer.color((1, 0, 0))
      renderer.xformXlate((-.85, 0, .15))
      renderer.xformRotate(self.u2deg(self.getValByName("LShoulder Rot")), \
                           (1, 0, 0))
      renderer.xformRotate(self.u2deg(self.getValByName("LShoulder Pron")), \
                           (0, 0, 1))
                           
      renderer.box((-.1, .1, -1), \
                   (.1, .1, -1), \
                   (.1, -.1, -1), \
                   (-.1, .1, 0))

      #Start Left Forearm
      renderer.xformPush()
      renderer.color((.6, 0 , 0))
      renderer.xformXlate((0, 0, -1))
      renderer.xformRotate(self.u2deg(self.getValByName("LElbow Rot")), \
                           (1, 0, 0))
      renderer.xformRotate(self.u2deg(self.getValByName("LElbow Pron")), \
                           (0, 0, 1))
      renderer.box((-.08, .08, -1), \
                   (.08, .08, -1), \
                   (.08, -.08, -1), \
                   (-.08, .08, 0))

      #Start Left Hand
      renderer.xformPush()
      renderer.color((.3, 0, 0))
      renderer.xformRotate(180, (0, 0, 1))
      renderer.xformXlate((0, 0, -1))
      renderer.xformRotate(self.u2deg(self.getValByName("LWrist Rot")), \
                           (0, 1, 0))
      renderer.box((-.1, .12, -.3), \
                   (.1, .12, -.3), \
                   (.1, -.12, -.3),
                   (-.1, .12, 0))

      #Start Left Index Finger
      renderer.xformPush()
      renderer.color((.2, 0, self.getValByName("LIndex")))
      renderer.xformXlate((.05, -.09, -.3))
      renderer.box((-.035, .035, -.25), \
                   (.035, .035, -.25), \
                   (.035, -.035, -.25), \
                   (-.035, .035, 0))
      renderer.xformPop() #End Left Index Finger

      #Start Left Pinky
      renderer.xformPush()
      renderer.color((.2, 0, self.getValByName("LPinky")))
      renderer.xformXlate((.05, .09, -.3))
      renderer.box((-.035, .035, -.25), \
                   (.035, .035, -.25), \
                   (.035, -.035, -.25), \
                   (-.035, .035, 0))
      renderer.xformPop() #End Left Pinky

      #Start Left Thumb
      renderer.xformPush()
      renderer.color((.2, 0, self.getValByName("LThumb")))
      renderer.xformXlate((-.05, 0, -.3))
      renderer.box((-.035, .035, -.2), \
                   (.035, .035, -.2), \
                   (.035, -.035, -.2), \
                   (-.035, .035, 0))
      renderer.xformPop() #End Left Thumb
      
      renderer.xformPop() #End Left Hand
      renderer.xformPop() #End Left Forearm
      renderer.xformPop() #End Left UpperArm
      
      #Start Right Upper Arm
      renderer.xformPush()
      renderer.color((0, 1, 0))
      renderer.xformXlate((.85, 0, .15))
      renderer.xformRotate(self.u2deg(self.getValByName("RShoulder Rot")), \
                           (1, 0, 0))
      renderer.xformRotate(self.u2deg(self.getValByName("RShoulder Pron")), \
                           (0, 0, 1))
                           
      renderer.box((-.1, .1, -1), \
                   (.1, .1, -1), \
                   (.1, -.1, -1), \
                   (-.1, .1, 0))

      #Start Right Forearm
      renderer.xformPush()
      renderer.color((0 , .6, 0))
      renderer.xformXlate((0, 0, -1))
      renderer.xformRotate(self.u2deg(self.getValByName("RElbow Rot")), \
                           (1, 0, 0))
      renderer.xformRotate(self.u2deg(self.getValByName("RElbow Pron")), \
                           (0, 0, 1))
      renderer.box((-.08, .08, -1), \
                   (.08, .08, -1), \
                   (.08, -.08, -1), \
                   (-.08, .08, 0))

      #Start Right Hand
      renderer.xformPush()
      renderer.color((0, .3, 0))
      renderer.xformXlate((0, 0, -1))
      renderer.xformRotate(self.u2deg(self.getValByName("RWrist Rot")), \
                           (0, 1, 0))
      renderer.box((-.1, .12, -.3), \
                   (.1, .12, -.3), \
                   (.1, -.12, -.3),
                   (-.1, .12, 0))

      #Start Right Index Finger
      renderer.xformPush()
      renderer.color((0, .2, self.getValByName("RIndex")))
      renderer.xformXlate((.05, -.09, -.3))
      renderer.box((-.035, .035, -.25), \
                   (.035, .035, -.25), \
                   (.035, -.035, -.25), \
                   (-.035, .035, 0))
      renderer.xformPop() #End Right Index Finger

      #Start Right Pinky
      renderer.xformPush()
      renderer.color((0, .2, self.getValByName("RPinky")))
      renderer.xformXlate((.05, .09, -.3))
      renderer.box((-.035, .035, -.25), \
                   (.035, .035, -.25), \
                   (.035, -.035, -.25), \
                   (-.035, .035, 0))
      renderer.xformPop() #End Right Pinky

      #Start Right Thumb
      renderer.xformPush()
      renderer.color((0, .2, self.getValByName("RThumb")))
      renderer.xformXlate((-.05, 0, -.3))
      renderer.box((-.035, .035, -.2), \
                   (.035, .035, -.2), \
                   (.035, -.035, -.2), \
                   (-.035, .035, 0))
      renderer.xformPop() #End Right Thumb
      
      renderer.xformPop() #End Right Hand
      renderer.xformPop() #End Right Forearm
      renderer.xformPop() #End Right UpperArm

      renderer.xformPop() #End Body

   def getOptions(self):
      pass

   def connect(self):
      pass

   def localize(self, x = 0.0, y = 0.0, z = 0.0):
      pass

   def disconnect(self):
      pass

   def loadDrivers(self):
      #What's with the Sense class and its subclasses?
      #They aren't used by saphira or khepera.  I just used
      #them as examples
      lld = ArmorLowlevel()
      self.drivers.append(ArmorSenseDriver(lld))
      self.drivers.append(ArmorControlDriver(lld))

   def SanityCheck(self):
      #Overriding Robot.SanityCheck
      pass

   def update(self):
      pass
   

       
