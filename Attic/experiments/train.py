"""
This progarm trains a som.
Names of the file need to be set
"""

from pyro.brain import psom
from pyro.brain.psom import vis
from pyro.brain.psom import *

mydataset = dataset(file = "collect.dat")
mysom = vis.VisPsom(20,15,data = mydataset)

mysom.init_training(0.02, 5, 5000000)
mysom.train_from_dataset(mydataset)
mysom.save_to_file("som20x15.cod")
print "Done!!!!"
mysom.win.mainloop()
