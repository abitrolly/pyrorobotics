# -------------------------------------------------------
# Sample Plotter
# -------------------------------------------------------

from Tkinter import *
import os

class SimplePlot: # based on Plot
    def __init__(self, robot, brain):
        self.win = Tk()
        self.robot = robot
        self.brain = brain
        self.win.wm_title("pyro@%s: Back Sensors" % os.getenv('HOSTNAME'))
        self.canvas = Canvas(self.win,width=400,height=120)
        self.canvas.pack()

        self.dataMin = 0
        self.dataMax = 2.99
        self.dataWindowSize = 400
        self.dataSample = 1
        self.dataCount = 0
        self.lastRun = 0
        self.dataHist = [0] * self.robot.get('sonar', 'count')

    def redraw(self, options):
        # do something to draw yourself
        if self.lastRun != self.brain.lastRun:
            self.lastRun = self.brain.lastRun
            colors = ['blue', 'red', 'tan', 'yellow', 'orange', 'black', 'azure', 'beige', 'brown', 'coral', 'gold', 'ivory', 'moccasin', 'navy', 'salmon', 'tan', 'ivory']
            if self.dataCount > self.dataWindowSize:
                self.canvas.delete('data')
                self.dataCount = 0
            else:
                self.dataCount += 1
            for sensor in self.robot.sensorGroups['back']:
                s, type = sensor
                dist = self.robot.get(type, 'value', s)
                if self.dataCount != 0:
                    self.canvas.create_line(self.dataCount - 1,
                                            self.dataHist[s],
                                            self.dataCount,
                                            int(float(dist)/self.dataMax * 100.0),
                                            tags = 'data',
                                            width = 2,
                                            fill = colors[s])
                self.dataHist[s] = int(float(dist)/self.dataMax * 100.0 - 1)

def INIT(robot, brain):
    return SimplePlot(robot, brain)
