# A Neural Network Brain
# D.S. Blank

# just reinforcement, for now, without prediction

from pyro.brain import Brain
from pyro.brain.conx import *
from pyro.gui.plot.scatter import *
from pyro.gui.plot.hinton import *
from random import random
from time import sleep
from pyro.brain.fuzzy import *


class Reinforce(Brain):
   def setup(self):
      '''Init the brain, and create the network'''
      self.net = SRN()
      self.sensorCount = self.getRobot().get('range', 'count')
      self.net.add(Layer('input', self.sensorCount+2))
      self.net.addContext(Layer('context', 2), 'hidden')
      self.net.add(Layer('hidden', 2))
      self.net.add(Layer('motorOutput', 2))
      self.net.add(Layer('sensorOutput', self.sensorCount))
      self.net.connect('input', 'hidden')
      self.net.connect('context', 'hidden')
      self.net.connect('hidden', 'motorOutput')
      self.net.connect('hidden', 'sensorOutput')

      self.net.setBatch(0)
      self.net.initialize()
      self.net.setVerbosity(0)
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.1)
      self.net.setLearning(1)

      self.counter = 0
      self.doneLearning = 0
      self.maxvalue = self.getRobot().get('range', 'maxvalue')
      self.curr_sensors = map(self.scale, self.getRobot().get('range', 'value', 'all'))
      self.curr_motors = [0.0, 0.0]
      self.target_trans = 1
      self.target_rotate = .5
      self.lastf = 0
      self.lastbest = 0
      self.weight = .5
      self.deltaw = .03
      
      self.plot = Scatter(title = 'Reinforce and Predict',
                          history = [100, 5, 5], linecount = 3,
                          legend = ['Hidden', 'Motor Output', 'Motor Target'])
      self.pred = Hinton(self.getRobot().get('range', 'count'),
                         title = 'Predicted Inputs')
      self.targ = Hinton(self.getRobot().get('range', 'count'),
                         title = 'Actual Inputs')

   def destroy(self):
      self.plot.destroy()
      self.pred.destroy()
      self.targ.destroy()
      del self.net
       
   def scale(self, val):
      '''scale val to fall between 0 and 1'''
      return (val / self.maxvalue)

   def step(self):
      '''
      everything else
      .input latest sensor and motor values to network
      .propagate
      .move by resulting motor output
      .set targets according to new sensor and motor values
      .backpropagate
      ''' 
      print self.counter
      
      if self.doneLearning:
         self.net.setLearning(0)
      else:
         self.net.setLearning(1)

      # gather inputs (latest sensors and motor values)
      self.curr_sensors = map(self.scale, self.getRobot().get('range', 'value', 'all'))
      input = (self.curr_sensors) 
      input.append(self.curr_motors[0])
      input.append(self.curr_motors[1])
      
      # set inputs
      if self.counter == 0:
         self.net.clearContext(.5)
      self.net.getLayer('input').copyActivations(input)

      # propagate...to see what output would be
      self.net.propagate()

      # move according to resulting motor outputs
      next_motors = self.net.getLayer('motorOutput').activation[:]
      trans = (next_motors[0] - .5)/2
      rotate = (next_motors[1] - .5)/2
      self.getRobot().move(trans, rotate)
      self.curr_motors = next_motors
      
      # set targets based on new sensor and motor values
      #    first set sensorOutput targets
      sleep(.1)
      self.getRobot().update()
      next_sensors = map(self.scale, self.getRobot().get('range', 'value', 'all'))
      self.net.getLayer('sensorOutput').copyTargets(next_sensors)

      #    next set motorOutput targets
      #       determine fuzzy values
      next_min = self.getRobot().get('range', 'value', 'all', 'min')[1]

      distance = Fuzzy(0,.8) >> self.scale(next_min) #used to be Fuzzy(0,1)
      speed = Fuzzy(.1,.4) >> abs(next_motors[0] - .5) #was Fuzzy(0,.5)
      fitness = distance & speed
      improvement = Fuzzy(-.1, .3) >> fitness() - self.lastf
      self.lastf = fitness()

      best = fitness | improvement
         
      #       determine weights for randomness
      if best() > .4:
         self.weight /= 4
      elif best()-self.lastbest >= .005:
         self.weight /= 2
      elif best()-self.lastbest <= -.005:
         self.weight += 1.5*self.deltaw
      elif best() < .4:
         self.weight += self.deltaw

      if self.weight > .75:
         self.weight = .75
      elif self.weight < 0:
         self.weight = 0
      
      self.lastbest = best()
      
      # compute and set motorOutput targets
      tt = self.PorM(next_motors[0], random()*self.weight)
      tr = self.PorM(next_motors[1], random()*self.weight)
      self.target_trans = max(min(tt, 1), 0)
      self.target_rotate = max(min(tr, 1), 0)
      # there is no backprop() between this an the last call of copyTarget()
      self.net.getLayer('motorOutput').copyTargets([self.target_trans,
                                                   self.target_rotate])
      
      # propagate backwards
      error = self.net.backprop() # will copy activations to context
      if not self.doneLearning:
         self.net.change_weights()
      
      # update plots
      self.plot.addPoint(next_motors[0], next_motors[1], 1)
      self.plot.addPoint(self.net.getLayer('hidden').activation[0],
                         self.net.getLayer('hidden').activation[1], 0)
      if not self.doneLearning:
         self.plot.addPoint(self.net.getLayer('motorOutput').target[0],
                            self.net.getLayer('motorOutput').target[1], 2)
      self.pred.update(self.net.getLayer('sensorOutput').activation)
      self.targ.update(self.net.getLayer('sensorOutput').target)

      # update counter
      self.counter += 1

   def PorM(self, a, b):
      if random() < .5:
         return a - b
      else:
         return a + b

def INIT(engine):
   return Reinforce('Reinforce', engine)
