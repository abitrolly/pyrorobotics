from pyro.gui.plot import *

def INIT(robot, brain):
   sensorList = map(lambda(x): x[0], robot.sensorGroups['left'])
   return GeneralPlot(robot, brain, sensorList,
                      name='Left Plot...General',
                      history = 300)
                      
