""" This is the FSM of the whole maze. """

from pyrobot.brain.behaviors import State, FSMBrain
from pyrobot.simulators.pysim import *
import random, time

def f2m(feet):
   """ feet to meters """
   return 0.3048 * feet
def cm2m(cm):
   """ feet to meters """
   return  cm / 100.0
def d2r(degrees):
   """ degrees to radians """
   return PIOVER180 * degrees

def avg(mem):
   return sum(mem)/len(mem)
      
##    def update(self):
##       self.sim.step(run=0)
##       self.sim.update()

class Start(State):
   def setup(self):
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      self.robot.frequency[0].setSampleTime(0.1)
      if not self.robot.hasA("camera"):
         #self.startDevice("V4LCamera0")
         #self.startDevice("BlimpMovie")
         self.startDevice("BlimpCameraHallway")
         self.startDevice("FourwayRot2")
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[1].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[1].addFilter("rotate",) # backview
        
   def step(self):
      self.engine.gui.makeWindows()
      self.robot.camera[4].setVisible(0)
      self.robot.camera[0].setVisible(0)
      print "Here we go!"
      self.goto("MaintainHeight")
      #self.goto("ReadFiducial")

class MaintainHeight(State):
   def setup(self):
      self.targetDistance = 1.0 # meters
      self.mem = [0]*10
      self.step_count = 0
      self.cont_count = 0
      self.old_amt = 0
      self.igain = 0.0
      self.pgain = 0.75
      self.dgain = 0.25
      self.integral = 0.0
      self.old_diff = 0.0
      self.deriv = 0.0
      self.pulseTime = 0.5
      self.dutyCycle = .3
      print "sleep between:", self.robot.frequency[0].asyncSleep
      print "sampleTime:", self.robot.frequency[0].sampleTime
      for i in range(10):
         distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
         self.mem[i] = distance
         time.sleep(.1)
         
   def step(self):
      distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
      av = avg(self.mem)
      #print abs(distance - av)
      if(abs(distance - av) > 1):
         self.cont_count += 1
         if(self.cont_count > 20):
            for i in range(10):
               distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
         return
      else:
         self.cont_count = 0
         self.mem[self.step_count%10] = distance
         self.step_count += 1
         #proportional
         diff = self.targetDistance - distance
         #print diff
         #integral
         self.integral += diff
         #derivative
         self.deriv = diff - self.old_diff
         #correction amount
         amount = (self.integral * self.igain + diff + (self.deriv*self.dgain)) * self.pgain
         if((amount >= 0) and (amount <= 19)):
            amount += 19
         elif((amount < 0) and (amount >= -19)):
            amount -= 19
         amount = max(min(amount, 1.0), -1.0)
         #print distance, amount, diff, self.pgain, self.igain, self.dgain
         self.old_amt = amount
         self.robot.moveZ(amount)
         time.sleep(.2)
         self.robot.moveZ(0) # ok, robot will do this automatically
         time.sleep(.2)
         #time.sleep(self.dutyCycle * self.pulseTime)
         #self.robot.moveZ(0.0)
         #time.sleep(self.pulseTime * (1-self.dutyCycle))
         self.old_diff = diff

class Search(State): # looking through forward camera to find a fiducial
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("match", 245, 193, 188, 25) #front view look for red
      self.robot.camera[3].addFilter("superColor", 0) #front view look for red
      self.robot.camera[3].addFilter("blobify", 0) #front view look for red
      self.robot.camera[2].addFilter("match", 158, 110, 99, 25) #front view look for red
      self.robot.camera[2].addFilter("superColor", 0) #front view look for red
      self.robot.camera[2].addFilter("blobify", 0) #front view look for red
      self.h1 = self.robot.camera[2].height
      self.h1L = self.h1/3
      self.counter = 0
      
   def step(self):
      self.counter += 1
      x1, y1, x2, y2, matches = self.robot.camera[2].filterResults[2][0]
      if matches > 100: # FIX: box is big enough?
         self.goto('GotoBullseye')
         return
      if matches > 50: # FIX: box is big enough?
         self.goto('Advance2Fid')
         return
      x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[2][0]
      if matches > 20:
         self.goto('Advance2Fid')
         return
      if random.random() < .3:
         if self.brain.robotControl:
            self.robot.move(.2, 0) # turn to the right
            time.sleep(6)
            self.robot.move(0, 0)
      if random.random() < .3:
         if self.brain.robotControl:
            self.robot.move(0, -.2) # turn to the right
            time.sleep(.1)
            self.robot.move(0, 0)
            time.sleep(.3)
      elif self.counter > 100:
         self.counter = 0
         if self.brain.robotControl:
            self.robot.move(.5,0) # go forward
            time.sleep(1)
            self.robot.move(0,0)

class Advance2Fid(State): # move towards Fiducial
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(1,0)
         time.sleep(1)
         self.robot.move(0,0)
   def step(self):
      self.goto('OrientFiducial')

class OrientFiducial(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      # use filters below
      self.counter = 0
        
   def step(self):
      self.counter += 1
      distance = self.robot.frequency[0].results[0]
      r1 = self.robot.camera[3].apply("grayScale")
      r2 = self.robot.camera[3].apply("orientation", distance)
      r3 = self.robot.camera[3].apply("superColor", 0)
      r4 = self.robot.camera[3].apply("blobify", 0)
      x1, y1, x2, y2, matches = r4
      if matches > 20: # FIX what is a good color?
         self.goto("ReadFiducial")
         return
      x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[3][0]
      cx, cy = (x1 + x2)/2, (y1 + y2)/2
      if self.brain.robotControl:
         if cx < self.robot.camera[3].width/2: # need to turn left
            self.move(0, .2)
         else: # turn some right
            self.move(0, -.2)
         if cy < self.robot.camera[3].height/2: # need to backup
            self.move(-.2, 0)
         else: # go forward
            self.move(.2, 0)
      if self.counter > 100:
         self.goto("Search")
       
class ReadFiducial(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("fid",)    # downview
      self.counter = 0
      self.fidC1 = 0
      self.fidC2 = 0
      self.fidC3 = 0
        
   def step(self):
      # looking if over fiducial
      self.h3 = self.robot.camera[3].height
      #self.w3 = self.robot.camera[3].width
      self.h3U = self.h3 - (self.h3/3)
      self.h3L = self.h3 - (2*(self.h3/3))
      self.fid3x, self.fid3y, self.fid3dots = self.robot.camera[3].filterResults[0]
    
      if self.fid3y > self.h3L and self.fid3y < self.h3U:
         if self.fid3dots == 1:
            self.fidC1 += 1
         elif self.fid3dots == 2:
            self.fidC2 += 1
         elif self.fid3dots == 3:
            self.fidC3 += 1

      if self.fidC1 > 5 or self.fidC2 > 5 or self.fidC3 > 5:
         maxval = max(self.fidC1, self.fidC2, self.fidC3)
         if maxval == self.fidC1:
            self.brain.map.decide(1)
            self.goto('Advance2ft1')
         elif maxval == self.fidC2:
            self.brain.map.decide(2)
            self.goto('Advance2ft2')
         elif maxval == self.fidC3:
            self.brain.map.decide(3)
            self.goto('Advance2ft3')
         self.FFcounter = 0
         return
         
      if self.counter > 100:
         self.goto('Search')  #### put returns after gotos
      else:
         self.counter +=1

class Advance2ft1(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(0,0) # stop
         self.robot.move(.2,0) # go forward 2 ft
         time.sleep(6)
         self.robot.move(0,0)
         self.robot.move(0,.2) # turn left
         time.sleep(2)
         self.robot.move(0,-.2) # stop turning
         time.sleep(.2)
         self.robot.move(.2,0) # go forward a few feet
         time.sleep(6)
         self.robot.move(0,0) # stop
   def step(self):
      self.goto('Search')

class Advance2ft2(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(0,0) # stop
         self.robot.move(.2,0) # go forward 2 ft
         time.sleep(6)
         self.robot.move(0,0) # stop
         time.sleep(1)
         self.robot.move(.2,0) # go forward a few feet
         time.sleep(6)
         self.robot.move(0,0) # stop
   def step(self):
      self.goto('Search')

class Advance2ft3(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(0,0) # stop
         self.robot.move(.2,0) # go forward 2 ft
         time.sleep(6)
         self.robot.move(0,0)
         self.robot.move(0,-.2) # turn left
         time.sleep(2)
         self.robot.move(0,.2) # stop turning
         time.sleep(.2)
         self.robot.move(.2,0) # go forward a few feet
         time.sleep(6)
         self.robot.move(0,0) # stop
   def step(self):
      self.goto('Search')
        
class Done(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
   def step(self):
      print "We're done! Look through window!"
      if self.brain.robotControl:
         self.robot.move(0,0)

class GotoBullseye(State):
   def onActivate(self): # method called when activated or gotoed
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("match", 245, 193, 188, 25) #front view look for red
      self.robot.camera[3].addFilter("superColor", 0) #front view look for red
      self.robot.camera[3].addFilter("blobify", 0) #front view look for red
      self.robot.camera[2].addFilter("match", 158, 110, 99, 25) #front view look for red
      self.robot.camera[2].addFilter("superColor", 0) #front view look for red
      self.robot.camera[2].addFilter("blobify", 0) #front view look for red
      self.counter = 0
      self.lost = 0

   def step(self):
      self.counter += 1
      if self.robot.camera[3].filterResults[2][0][4] > 20: # matches ///
         self.goto("HoverBullseye")
         return
      x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[2][0]
      cx, cy = (x1 + x2)/2, (y1 + y2)/2
      if matches == 0:
         self.lost += 1
      if self.lost > 20:
         self.goto("Search")
         return
      if self.brain.robotControl:
         if cx < self.robot.camera[3].width/2: # need to turn left
            self.move(0, .2)
         else: # turn some right
            self.move(0, -.2)
         if cy < self.robot.camera[3].height/2: # need to backup
            self.move(-.2, 0)
         else: # go forward
            self.move(.2, 0)
      if self.counter > 100:
         self.goto('Search')  #### put returns after gotos


class HoverBullseye(State):
   def onActivate(self): # method called when activated or gotoed
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("match", 245, 193, 188, 25) #front view look for red
      self.robot.camera[3].addFilter("superColor", 0) #front view look for red
      self.robot.camera[3].addFilter("blobify", 0) #front view look for red
      self.startTime = time.time()
      self.lost = 0
    
   def step(self):
      if time.time() - self.startTime > 15:
         self.goto('Done')
      else:
         x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[2][0]
         cx, cy = (x1 + x2)/2, (y1 + y2)/2
         if matches == 0:
            self.lost += 1
         if self.lost > 10:
            self.goto('Search')            
         if self.brain.robotControl:
            if cx < self.robot.camera[3].width/2: # need to turn left
               self.move(0, .2)
            else: # turn some right
               self.move(0, -.2)
            if cy < self.robot.camera[3].height/2: # need to backup
               self.move(-.2, 0)
            else: # go forward
               self.move(.2, 0)

class MyBrain(FSMBrain):
   def setup(self):
      self.robotControl = 0


def INIT(engine): # passes in engine, if you need it
   brain = MyBrain("Blimpy", engine)
   # add a few states:
   brain.add(Start(1))
   brain.add(MaintainHeight()) # will always be on after Start
  ##  brain.add(Search())
##    brain.add(Advance2Fid())
##    brain.add(OrientFiducial())
##    brain.add(ReadFiducial())
##    brain.add(Advance2ft1())
##    brain.add(Advance2ft2())
##    brain.add(Advance2ft3())
##    brain.add(Done())
##    brain.add(GotoBullseye())
##    brain.add(HoverBullseye())
   return brain

if __name__ == "__main__":
   pass
