from pyro.gui.plot.simple import SimplePlot

def INIT(engine, brain = 0):
    return SimplePlot(engine.robot, 'front-all')
