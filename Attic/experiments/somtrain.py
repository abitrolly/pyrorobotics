"""
This progarm trains a som.
Names of the file need to be set
"""

from pyro.brain import psom
#from pyro.brain.psom import vis
from pyro.brain.psom import *
from pyro.gui.plot.hinton import *

cameraDataSet = dataset(file = "camera.dat")
cameraSom = psom(20,15,data = cameraDataSet)
cameraSom.init_training(0.2, 5, 1000000)
cameraSom.train_from_dataset(cameraDataSet)
cameraSom.save_to_file("camera-200passes-20x15.cod")
print "Camera Done!!!!"

sonarDataSet = dataset(file = "sonar.dat")
sonarSom = psom(20,15,data = sonarDataSet)
sonarSom.init_training(0.2, 5, 1000000)
sonarSom.train_from_dataset(sonarDataSet)
sonarSom.save_to_file("sonar-200passes-20x15.cod")
print "Sonar Done!!!!"


