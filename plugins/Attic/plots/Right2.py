from pyro.gui.plot import *

def INIT(robot, brain):
   sensorList = map(lambda(x): x[0], robot.sensorGroups['right'])
   return GeneralPlot(robot, brain, sensorList,
                      name='Right Plot...General',
                      history = 300)
                      
