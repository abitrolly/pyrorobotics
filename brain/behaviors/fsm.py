# FSM code

from pyrobot.brain import Brain

class FSMBrain (Brain):
   """
   This is the main engine that runs the FSM.
   """
   def __init__(self, engine = 0):
      Brain.__init__(self, 'FSMBrain', engine)
      self.states = {}
      self.robot = self.engine.robot

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
      state.robot = self.engine.robot
      state.brain = self
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
      self.debug = 0
      self.behaviors = {}
      self.activatelist = []
      self.deactivatelist = []
      self.status = status
      self.type = self.__class__.__name__
      self.name = name or self.type

   def getState(self, statename):
      if statename in self.brain.states.keys():
         return self.brain.states[statename]
      else:
         raise "ERROR: no such statename"
   def goto(self, state, *args):
      if self.debug:
         print "Leaving state '%s'; going to state '%s'..." % (self.name, state)
      self.deactivate(self.name)
      self.activate(state)
      self.brain.states[state].onGoto(args)
      self.brain.goto(state)
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
      pass
   def setup(self):
      pass # normally will overload
   def onDeactivate(self):
      pass # normally will overload
   def update(self):
      self.step()
   def step(self):
      pass # normally will overload
   def add(self, b):
      if b.name in self.behaviors.keys():
         raise "ERROR: beh already exists: '" + b.name + "'"
      else:
         self.behaviors[b.name] = b
      # keep a pointer to parent engine, from the beh:
      b.engine = self.engine
      b.brain = self.engine.brain
      b.robot = self.engine.robot
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
               self.brain.desires.append( r )
               # what is the controller effect for this state/behavior?
               self.brain.effectsTotal[b.state.name+":"+b.name+":"+r[1]] = b.effects[r[1]]
      self.update()

   def push(self, statename = None):
      if statename == None:
         statename = self.name
      if statename not in self.brain.states:
         raise AttributeError, "push: not a valid state name '%s'" % statename
      self.brain.stack.append( statename )

   def pop(self):
      if len(self.brain.states) > 0:
         returnState = self.brain.stack.pop()
         self.goto(returnState)
      else:
         raise AttributeError, "pop without a push in state '%s'" % self.name

   # wrappers here to talk to default robot:
   def set(self, path, value):
      return self.robot.set(path, value)
   def get(self, *args):
      return self.robot.get(*args)
   def move(self, *args):
      return self.robot.move(*args)
   def translate(self, *args):
      return self.robot.translate(*args)
   def rotate(self, *args):
      return self.robot.rotate(*args)
   def stop(self):
      return self.robot.stop()
   def startDevice(self, *args, **keywords):
      return self.robot.startDevice(*args, **keywords)
   def removeDevice(self, *args, **keywords):
      return self.robot.removeDevice(*args, **keywords)
   def motors(self, *args):
      return self.robot.motors(*args)
   def getDevice(self, *args):
      return self.robot.getDevice(*args)
   def hasA(self, *args):
      return self.robot.hasA(*args)
   def requires(self, *args):
      return self.robot.requires(*args)

