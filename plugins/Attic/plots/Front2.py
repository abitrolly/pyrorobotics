from pyro.gui.plot import *

def INIT(robot, brain):
   sensorList = map(lambda(x): x[0], robot.sensorGroups['front'])
   return GeneralPlot(robot, brain, sensorList,
                      name='Front Plot...General',
                      history = 300)
                      
