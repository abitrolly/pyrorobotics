# This is basically a rewrite of XRCL in Python
# BehaviorBased Brain

# defines the Behavior-based brain, behaviors, and states
import time
from pyro.brain import *
from pyro.brain.behaviors.fsm import State # State is not used here, but needed when you import this

class BehaviorBasedBrain(Brain):
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
      self.initialized = 0
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
      state.engine = self.engine
      state.brain = self
      state.setup()
      if state.status:
         state.onActivate()
   def reset(self):
      self.states = {}
      #self.status = -1
      self.desires = []
      self.effectsTotal = {}
   def step(self):
      if not self.initialized:
         for s in self.states.keys():
            self.states[s].setcontrols(self.controls)
         self.initialized = 1
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
         if totalTruth[c] != 0:
            part = ((d[0]*(self.effectsTotal[d[5]+":"+d[4]+":"+d[1]]/totalEffects[d[1]]))/totalTruth[c])
         else:
            part = 0
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
            #print "setting %s to value %f" % (c, control[c])
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
      time.sleep(0.01)
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
   def redrawPie(self, pie, percentSoFar, piececnt, controller,
                 percent, name):
      # FIX: behavior specific. How to put in Behavior-based code?
      xoffset = 5
      yoffset = 20
      width = 100
      row = (pie - 1) * (width * 1.5)
      colors = ['blue', 'red', 'tan', 'yellow', 'orange', 'black', 'azure', 'beige', 'brown', 'coral', 'gold', 'ivory', 'moccasin', 'navy', 'salmon', 'tan', 'ivory']
      self.canvas.create_text(xoffset + 60,row + 10, tags='pie',fill='black', text = controller) 
      self.canvas.create_arc(xoffset + 10,row + yoffset,width + xoffset + 10,row + width + yoffset,start = percentSoFar * 360.0, extent = percent * 360.0 - .001, tags='pie',fill=colors[(piececnt - 1) % 17])
      self.canvas.create_text(xoffset + 300,row + 10 + piececnt * 20, tags='pie',fill=colors[(piececnt - 1) % 17], text = name)

   def redraw(self):
      if len(self.pie) != 0:
         self.canvas.delete('pie')
         piecnt = 0
         for control in self.controls:
            piecnt += 1
            percentSoFar = 0
            piececnt = 0
            for d in self.pie:
               if control == d[0]:
                  piececnt += 1
                  portion = d[2]
                  try:
                     self.redrawPie(piecnt, percentSoFar, \
                                    piececnt, \
                                    "%s effects: %.2f" % \
                                    (d[0], self.history[0][d[0]]),
                                    portion, \
                                    "(%.2f) %s IF %.2f THEN %.2f = %.2f" % \
                                    (d[1], d[5], d[2], d[3], d[4]))
                  except:
                     pass
                  percentSoFar += portion
      else:
         self.canvas.create_text(200,130, tags='pie',fill='black', text = "Ready...")

class Behavior:
   """
   The core object. This gets subclassed for each beh instance
   """
   def __init__(self, status = 0, effects = {}, name = ''):
      self.status = status
      self.type = self.__class__.__name__
      self.name = name or self.type
      self.effects = effects
   def setup(self):
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
      return self.engine.robot
   def getEngine(self):
      return self.engine
   def getBrain(self):
      return self.brain

