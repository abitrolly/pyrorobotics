# Load in saved weights from offline training 
# Inputs are the two front sensor readings  
# Output is a translate value, used to control the robot  
   
from pyro.brain import Brain  
from pyro.brain.conx import *  
from time import *  
     
class NNBrain(Brain):  
   def setup(self):  
      self.n = Network()  
      self.n.addThreeLayers(8,1,2)  
      self.maxvalue = self.getRobot().get('range', 'maxvalue')  
      self.doneLearning = 1  
      self.n.loadWeightsFromFile("E05M01.wts")  
      self.n.setLearning(0)  
 
   def scale(self, val):  
      return min(max(val / self.maxvalue, 0.0),1.0) 
 
   def step(self):  
      robot = self.getRobot()  
      # Set inputs  
      sensors = robot.get('range', 'value', 'front')  
      self.n.getLayer('input').copyActivations( map(self.scale, sensors) ) 
      self.n.propagate()  
      translateActual = self.n.getLayer('output').activation[0]  
      rotateActual = self.n.getLayer('output').activation[1]  
      print "move", translateActual, rotateActual 
      robot.move(translateActual, rotateActual)  
   
def INIT(robot):  
   return NNBrain('NNBrain', robot)  
