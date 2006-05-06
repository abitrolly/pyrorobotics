""" This is the FSM of the whole maze. """

from pyrobot.brain.behaviors import State, FSMBrain
from pyrobot.simulators.pysim import *
import random, time

def f2m(feet):
   """ feet to meters """
   return 0.3048 * feet
def d2r(degrees):
   """ degrees to radians """
   return PIOVER180 * degrees

class Map:
   def __init__(self):
      # (width, height), (offset x, offset y), scale:
      self.sim = TkSimulator((411,651), (43,605), 27.229171, run = 0) 
      self.sim.wm_title("Indoor Aerial Robot Competition Map")
      # entry way:
      self.sim.addWall(f2m(17.3), f2m(0), f2m(17.3), f2m(11))
      self.sim.addWall(f2m(17.3 + 4), f2m(0), f2m(17.3 + 4), f2m(11))
      # angles:
      self.sim.addWall(f2m(17.3), f2m(11), f2m(0), f2m(21))
      self.sim.addWall(f2m(17.3 + 4), f2m(11), f2m(38), f2m(21))
      # sides:
      self.sim.addWall(f2m(0), f2m(21), f2m(0), f2m(21 + 45.7))
      self.sim.addWall(f2m(38), f2m(21), f2m(38), f2m(21 + 45.7 - 9.5))
      # far wall:
      # triangles:
      # fiducials:
      self.addFiducial(19.3, 17, 0)
      # robot:
      self.sim.addRobot(60000, TkBlimp("Blimpy", f2m(17.3 + 2), f2m(8), 0.0))
      # other things you can add:
      #self.sim.addShape("line", (5, 3), (6, 5), fill = "blue")
      #self.sim.addShape("polygon", (2, 3), (3, 2), (4, 3), fill = "red")
      #self.sim.addShape("oval", (5, 7), (6, 6), fill = "green")
      #self.sim.addShape("box", 5, 7, 6, 6, "purple")
      self.update()

   def move(self, x, y, z = 0):
      self.sim.robots[0].move(x, y)
      self.update()

   def moveTo(self, x, y, th):
      self.sim.robots[0]._gx = f2m(x)
      self.sim.robots[0]._gy = f2m(y)
      self.sim.robots[0]._ga = d2r(th)
      self.update()

   def addFiducial(self, x, y, th, dots = 3):
      xm = f2m(x)
      ym = f2m(y)
      thr = d2r(th)
      cos_a90 = math.cos(thr)
      sin_a90 = math.sin(thr)
      x1, y1 = (xm + f2m(2) * cos_a90 - 0 * sin_a90), (ym + f2m(2) * sin_a90 + 0 * cos_a90)
      x2, y2 = (xm - f2m(2) * cos_a90 - 0 * sin_a90), (ym - f2m(2) * sin_a90 + 0 * cos_a90)
      self.sim.addShape("line", (x1, y1), (x2, y2), fill="black") # long line
      # forks:
      px1, py1 = (xm + f2m(2) * cos_a90 - f2m(1) * sin_a90), (ym + f2m(2) * sin_a90 + f2m(1) * cos_a90)
      px2, py2 = (xm - f2m(2) * cos_a90 - f2m(1) * sin_a90), (ym - f2m(2) * sin_a90 + f2m(1) * cos_a90)
      self.sim.addShape("line", (x1, y1), (px1, py1), fill="black")
      self.sim.addShape("line", (x2, y2), (px2, py2), fill="black")
      # dots:
      if dots in (1, 3):
         x, y = (xm + f2m(0) * cos_a90 - f2m(.5) * sin_a90), (ym + f2m(0) * sin_a90 + f2m(.5) * cos_a90)
         self.sim.addShape("oval", (x - f2m(.3), y - f2m(.3)), (x + f2m(.3), y + f2m(.3)), fill="red")
      if dots in (2, 3):
         x, y = (xm - f2m(1) * cos_a90 - f2m(.5) * sin_a90), (ym - f2m(1) * sin_a90 + f2m(.5) * cos_a90)
         self.sim.addShape("oval", (x - f2m(.3), y - f2m(.3)), (x + f2m(.3), y + f2m(.3)), fill="red")
         x, y = (xm + f2m(1) * cos_a90 - f2m(.5) * sin_a90), (ym + f2m(1) * sin_a90 + f2m(.5) * cos_a90)
         self.sim.addShape("oval", (x - f2m(.3), y - f2m(.3)), (x + f2m(.3), y + f2m(.3)), fill="red")
      
   def update(self):
      self.sim.step(run=0)
      self.sim.update()

class Start(State):
   def setup(self):
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
         self.robot.frequency[0].setSampleTime(0.1)
      if not self.robot.hasA("camera"):
         #self.startDevice("V4LCamera0")
         self.startDevice("BlimpMovie")
         self.startDevice("FourwayRot2")
         self.robot.camera[1].addFilter("rotate",) # backview
         self.robot.camera[3].addFilter("fid",)    # downview
   def step(self):
      self.engine.gui.makeWindows()
      self.robot.camera[4].setVisible(0)
      self.robot.camera[0].setVisible(0)
      self.engine.gui.watch("brain.getStates()")
      self.engine.gui.watch("robot.camera[3].filterResults")
      print "RUNNING!"
      print "Enter: brain.states['Start'].go = 1"
      self.go = 0 
      while not self.go:
         self.robot.move(0, 0, 0)
      self.goto("MaintainHeight")
      self.goto("OrientFiducial")

class MaintainHeight(State):
   def setup(self):
      self.targetDistance = 1.0 # meters
      self.igain = 0.0
      self.pgain = 0.0
      self.dgain = 0.0
      self.integral = 0.0
      self.old_diff = 0.0
      self.deriv = 0.0
      print "sleep between:", self.robot.frequency[0].asyncSleep
      print "sampleTime:", self.robot.frequency[0].sampleTime
         
   def step(self):
      distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
      #proportional
      diff = self.targetDistance - distance
      #integral
      self.integral += diff
      #derivative
      self.deriv = diff - self.old_diff
      #correction amount
      amount = (self.integral * self.igain + diff + (self.deriv*self.dgain)) * self.pgain
      if(amount > 0):
         amount +=.19
      else:
         amount -=.19
      amount = max(min(amount, 1.0), -1.0)
      self.robot.moveZ(amount)
      self.old_diff = diff
      # if it is somewhat reliable, set the distance:
      self.robot.z = distance

class Search(State):
    def onActivate(self):
        self.FFcounter = 0
        self.slope = -1

    def step(self):
        # is there a big red blob?
        self.goto('HoverBullseye')
        # is there a black line?
        #get slope
        if 0: #self.slope > -1
            self.FFcounter = 0
            self.goto('OrientFiducial')
           
        if self.FFcounter > 100:
            # for xxx wait
            self.FFcount = 0
            self.FFcounter +=1
        
class OrientFiducial(State):
    def onActivate(self):
        self.counter = 0
        self.slope = 0

    def step(self):
        if self.slope !=0:
            # for xxx wait
            # turn nDegrees
            pass
        # read direction
        # for xxx wait
        # turn nDegrees
        self.goto('Search')
        
class Done(State):
    def onActivate(self):
        pass

    def step(self):
        pass

class HoverBullseye(State):
    def onActivate(self): # method called when activated or gotoed
        pass
    
    def step(self):
        # not seeing red for a bit,
        if random.random() < .1:
            self.goto('Done')
        else:
            self.goto('Search')
        # else keep centered on red

def INIT(engine): # passes in engine, if you need it
    brain = FSMBrain("Blimpy", engine)
    # add a few states:
    brain.add(Start(1))
    brain.add(MaintainHeight()) # will always be on after Start
    brain.add(OrientFiducial())
    brain.add(Search())
    brain.add(HoverBullseye())
    brain.add(Done())
    return brain

if __name__ == "__main__":
   mapper = Map()
