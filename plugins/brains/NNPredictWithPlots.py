# A Neural Network Brain
# D.S. Blank

# Not a true predictor but useful as a platform for testing the new Conx step method.

from pyro.brain import Brain
from pyro.brain.conx import *
from pyro.gui.plot.scatter import *
from pyro.gui.plot.hinton import *

class NNPredict(Brain):
   def setup(self):
      """ Create the network. """
      self.net = SRN()
      self.sensorCount = self.getRobot().get('range', 'count')
      self.net.add(Layer('input', self.sensorCount+2))
      self.net.addContext(Layer('context', 2), 'hidden')
      self.net.add(Layer('hidden', 2))
      self.net.add(Layer('prediction', self.sensorCount))
      self.net.add(Layer('motorOutput', 2))
      self.net.connect('input', 'hidden')
      self.net.connect('context', 'hidden')
      self.net.connect('hidden', 'prediction')
      self.net.connect('hidden', 'motorOutput')
      
      self.net.initialize()
      self.net.setVerbosity(0)
      self.net.setInitContext(0)
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.1)
      self.net.setLearning(1)

      self.new = [0]
      self.trans = 0
      self.rotate = 0
      self.counter = 0
      self.doneLearning = 0
      self.getRobot().set('range', 'units', 'METERS')
      self.maxvalue = self.getRobot().get('range', 'maxvalue')
      print " Max value: ", self.maxvalue
      
      self.plot1 = Scatter()
      self.plot1.setTitle('translate x rotate')
      self.plot2 = Scatter()
      self.plot2.setTitle('hidden 0 x hidden 1')
      self.plot3 = Scatter()
      self.plot3.setTitle('targetT x targetR')
      self.pred = Hinton(self.getRobot().get('range', 'count'),
                         title = 'Predicted Inputs')
      self.targ = Hinton(self.getRobot().get('range', 'count'),
                         title = 'Actual Inputs')
      self.cont = Hinton(2, title = 'Context Layer')
      self.hidd = Hinton(2, title = 'Hidden Layer')

   def destroy(self):
      self.plot1.destroy()
      self.plot2.destroy()
      self.plot3.destroy()
      self.pred.destroy()
      self.targ.destroy()
      self.hidd.destroy()
      self.cont.destroy()
      del self.net
      
   def scale(self, val):
      return (val / self.maxvalue)           
    
   def step(self):
      if self.counter > 10000:
         self.doneLearning = 1
         self.net.setLearning(0)
      else:
         print self.counter

      # set targets   
      target_rotate = 0.5
      if self.getRobot().get('range', 'value', 'front', 'min')[1] < .5:
         target_trans = 0.0
         target_rotate = 0.0 # some asymmetry to make things interesting
      elif self.getRobot().get('range', 'value', 'back', 'min')[1] < .5:
         target_trans = 1.0
      else:
         target_trans = 1.0
      if self.getRobot().get('range', 'value', 'left', 'min')[1] < .2:
         target_rotate = 0.0
      elif self.getRobot().get('range', 'value', 'right', 'min')[1] < .2:
         target_rotate = 1.0
      else:
         pass
      target = [target_trans,target_rotate]

      # print "Raw sensor data: ", self.getRobot().get('range', 'value', 'all')
      # print "Context Layer: ", self.net.getLayer('context').activation
      # print "Hidden Layer: ", self.net.getLayer('hidden').activation

      self.cont.update(self.net.getLayer('context').activation)
      self.hidd.update(self.net.getLayer('hidden').activation)
      
      # set up inputs and learn
      if self.counter == 0:
         self.new = map(self.scale, self.getRobot().get('range', 'value', 'all'))
         #self.net.clearContext() # do once
      else:
         old = self.new + [self.trans, self.rotate] #trans and rotate
         self.new = map(self.scale, self.getRobot().get('range', 'value', 'all'))
         # print self.new
         self.net.step( input = old, motorOutput = target, prediction = self.new )

      # results
      self.trans = self.net.getLayer('motorOutput').activation[0]
      self.rotate = self.net.getLayer('motorOutput').activation[1]

      self.getRobot().move((self.trans - .5)/2.0, (self.rotate - .5)/2.0)

      self.plot1.addPoint(self.trans, self.rotate)
      self.plot2.addPoint(self.net.getLayer('hidden').activation[0],
                          self.net.getLayer('hidden').activation[1])
      self.plot3.addPoint(target_trans, target_rotate)
      self.pred.update(self.net.getLayer('prediction').activation)
      self.targ.update(self.net.getLayer('prediction').target)

      self.counter += 1

def INIT(engine):
   return NNPredict('NNPredict', engine)
      
