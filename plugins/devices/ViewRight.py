from pyro.gui.plot.simple import SimplePlot

def INIT(robot):
    return {"view": SimplePlot(robot, 'right')}
