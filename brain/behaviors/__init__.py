# This is basically a rewrite of XRCL in Python
# BehaviorBased Brain

# defines the Behavior-based brain, behaviors, and states

from time import *
from pyro.brain import *

class BehaviorBasedBrain (Brain):
   """
   This is the main engine that runs collections of behaviors (states).
   Usually, you create once of these per robot.
   """
   def __init__(self, controllers = {}, engine = 0):
      Brain.__init__(self, 'BehaviorBasedBrain', engine)
      self.states = {}
      self.controls = controllers
      self.history = [{}, {}, {}]
      self.pie = []
      self.desires = []
      self.effectsTotal = {}
   def set_controls(self, controllers):
      self.controls = controllers
      self.history = [{}, {}, {}]
   def activate(self, name):
      self.states[name].status = 1
      self.states[name].onActivate()
   def deactivate(self, name):
      self.states[name].status = 0
      self.states[name].onDeactivate()
   def add(self, state):
      if state.name in self.states.keys():
         raise "ERROR: state already exists: '" + state.name + "'"
      self.states[state.name] = state
      state.behaviorEngine = self
      state.init()
      if state.status:
         state.onActivate()
   def reset(self):
      self.states = {}
      #self.status = -1
      self.desires = []
      self.effectsTotal = {}
   def init(self): # init and get ready to run
      for s in self.states.keys():
         self.states[s].setcontrols(self.controls)
      #if self.status == -1: # virgin, need to init states
      #self.status = 1 # be is read to run
   def step(self):
      #self.init() # init if necessary
      self.desires = [] # init all desires (this will be set in state.run)
      self.history[2] = self.history[1]
      self.history[1] = self.history[0]
      self.history[0] = {}
      self.effectsTotal = {}
      for s in self.states.keys():
         if self.states[s].status == 1:
            self.states[s].run()
      # desires: truth, controller, value, rulename, behname, statename
      control = {}
      # set all totalTruths to 0, totalEffects to 0
      totalTruth = {}
      totalEffects = {}
      for c in self.controls.keys():
         totalTruth[c] = 0.0
         totalEffects[c] = 0.0
      for e in self.effectsTotal.keys(): # state:beh:controller
         s, b, c = e.split(':')
         totalEffects[c] = max(float(self.effectsTotal[e]), totalEffects[c])
      # sum up totalTruth
      for d in self.desires: 
         # compute total truth for each controller
         totalTruth[d[1]] += d[0] * (self.effectsTotal[d[5]+":"+d[4]+":"+d[1]] / totalEffects[d[1]])
      self.pie = []
      for d in self.desires: 
         # (beffect / totaleffect) * (truth / totaltruth) * value
         c = d[1]
         part = ((d[0]*(self.effectsTotal[d[5]+":"+d[4]+":"+d[1]]/totalEffects[d[1]]))/totalTruth[c])
         amt = part * d[2]
         self.pie.append( [d[1], (self.effectsTotal[d[5] + ":" + d[4] + ":" + c] / totalEffects[c]),
                           part, d[2], amt,
                           d[5] + ":" + d[4] + ":" + d[3] ] )
                          
         if c in control.keys():
            control[c] += amt
         else:
            control[c] = amt
      for c in self.controls.keys():
         if c in control.keys():
            # set that controller to act with a value
            self.controls[c](control[c])
            self.history[0][c] = control[c]
      # -------------------------------------------------
      # This will update robot's position so that the GUI
      # can draw it, even if no command is sent to move
      # the robot. 
      # -------------------------------------------------
      self.controls['update']()
      # -------------------------------------------------
      # let's force a 0.1s break so that we are going to have
      # at most 10 cycles per second
      # an improved version is expected
      # -------------------------------------------------
      sleep(0.01)
      # change states' status if necessary
      for s in self.states.keys():
         for d in self.states[s].deactivatelist: #deactivate first
            self.deactivate(d)
         for a in self.states[s].activatelist:
            self.activate(a)
         self.states[s].activatelist = []
         self.states[s].deactivatelist = []
   def stop_all(self):
      for c in self.controls.keys():
         # set that controller to act with a value
         self.controls[c](0)

class Behavior:
   """
   The core object. This gets subclassed for each beh instance
   """
   def __init__(self, status = 0, effects = {}, name = ''):
      self.status = status
      self.type = self.__class__.__name__
      self.name = name or self.type
      self.effects = effects
   def init(self):
      pass # this will get over written, normally
   def onActivate(self):
      pass
   def onDeactivate(self):
      pass
   def update(self):
      pass # this will get over written, normally
   def Effects(self, controller, amount = 1.0):
      self.effects[controller] = amount
   def IF(self, fvalue, controller, amount = 1.0, name = ''):
      if name == '':
         name = "Rule%d" % (len(self.rules) + 1)
      self.rules.append([float(fvalue), controller, float(amount), name])
   def getRobot(self):
      return self.behaviorEngine.robot

class State:
   """
   Collections of behaviors. this gets subclassed by each collection
   """
   def __init__(self, status = 0, name = ''):
      self.behaviors = {}
      self.activatelist = []
      self.deactivatelist = []
      self.status = status
      self.type = self.__class__.__name__
      self.name = name or self.type
   def getState(self, statename):
      if statename in self.behaviorEngine.states.keys():
         return self.behaviorEngine.states[statename]
      else:
         raise "ERROR: no such statename"
   def goto(self, state, *args):
      self.deactivate(self.name)
      self.activate(state)
      self.behaviorEngine.states[state].onGoto(args)
   def onGoto(self, args = []):
      # FIX: could make a nice way of setting class vars here.
      # Currently:
      # if you pass this vars, you must take care of them!
      pass # normally will overload
   def activate(self, name):
      if not (name in self.activatelist):
         self.activatelist.append(name)
   def deactivate(self, name):
      if not (name in self.deactivatelist):
         self.deactivatelist.append(name)
   def onActivate(self):
      pass # normally will overload
   def onDeactivate(self):
      pass # normally will overload
   def update(self):
      pass # normally will overload
   def init(self):
      pass # normally will overload
   def add(self, b):
      if b.name in self.behaviors.keys():
         raise "ERROR: beh already exists: '" + b.name + "'"
      else:
         self.behaviors[b.name] = b
      # keep a pointer to parent engine, from the beh:
      b.behaviorEngine = self.behaviorEngine
      # keep a pointer to parent state, from the beh:
      b.state = self
      b.init() # init the behavior, just once
      if b.status:
         b.onActivate()
   def setcontrols(self, controls):
      self.controls = controls
   def run(self):
      for bkey in self.behaviors.keys():
         b = self.behaviors[bkey]
         if b.status:
            b.rules = [] # clear rules
            b.update() # fires IF rules
            for r in b.rules:
               # r = truth, controller, amount, beh name, state name
               r.extend([b.name, b.state.name])
               self.behaviorEngine.desires.append( r )
               # what is the controller effect for this state/behavior?
               self.behaviorEngine.effectsTotal[b.state.name+":"+b.name+":"+r[1]] = b.effects[r[1]]
      self.update()

   def getRobot(self):
      return self.behaviorEngine.robot
