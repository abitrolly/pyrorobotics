from pyro.brain import psom 
from pyro.brain.psom import vis

import random 
 
def randomBit(): 
  if random.random() < 0.5: 
     return 0 
  else: 
     return 1 
 
def randomVec(n): 
  vec = [0] * n
  vec[int(random.random() * n)] = 1
  return vec 

mysom = vis.VisPsom(2, 10, dim=10)
mysom.init_training(0.02, 3, 10000)

for i in range(10000): 
  vec = randomVec(10) 
  #print vec 
  model = mysom.train(psom.vector(vec)) 

