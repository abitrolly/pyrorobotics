"""
This progarm trains a som.
Names of the file need to be set
"""

from pyro.brain import psom
from pyro.brain.psom import vis
from pyro.brain.psom import *
from pyro.gui.plot.hinton import *

mydataset = dataset(file = "camera.dat")
mysom = vis.VisPsom(20,15,data = mydataset, vis_vectortype = 'Matrix', opts=(60,15))

mysom.init_training(0.02, 5, 100000)
mysom.train_from_dataset(mydataset)
mysom.save_to_file("camera-20passes-20x15.cod")
print "Done!!!!"
mysom.win.mainloop()
