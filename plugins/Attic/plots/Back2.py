from pyro.gui.plot import *

def INIT(robot, brain):
   sensorList = map(lambda(x): x[0], robot.sensorGroups['back'])
   return GeneralPlot(robot, brain, sensorList,
                      name='Back Plot...General',
                      history = 300)
                      
