""" This is the FSM of the whole maze. """

from pyrobot.brain.behaviors import State, FSMBrain
import random

class Start(State):
   def step(self):
      print "To start: brain.states['Start'].go = 1"
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
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      self.robot.frequency[0].setSampleTime(0.1)
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
