# FSM code

from pyro.brain import Brain

class FSMBrain (Brain):
   """
   This is the main engine that runs the FSM.
   """
   def __init__(self, engine = 0):
      Brain.__init__(self, 'FSMBrain', engine)
      self.states = {}

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
      state.setup()
      if state.status:
         state.onActivate()

   def reset(self):
      self.states = {}

   def step(self):
      for s in self.states.keys():
         if self.states[s].status == 1:
            self.states[s].run()
      # pause?
      for s in self.states.keys():
         for d in self.states[s].deactivatelist: #deactivate first
            self.deactivate(d)
         for a in self.states[s].activatelist:
            self.activate(a)
         self.states[s].activatelist = []
         self.states[s].deactivatelist = []

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
   def setup(self):
      pass # normally will overload
   def add(self, b):
      print b
      print b.name
      print self.behaviors
      if b.name in self.behaviors.keys():
         raise "ERROR: beh already exists: '" + b.name + "'"
      else:
         self.behaviors[b.name] = b
      # keep a pointer to parent engine, from the beh:
      b.behaviorEngine = self.behaviorEngine
      # keep a pointer to parent state, from the beh:
      b.state = self
      b.setup() # init the behavior, just once
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

   def getEngine(self):
      return self.behaviorEngine.getEngine()

