from pyro.gui.plot import *

def INIT(robot, brain):
   sensorList = [2, 3]
   return GeneralPlot(robot, brain, sensorList,
                      sensorType='ir',
                      name='Front Plot...Khepera',
                      maxVal=60)
                      
