# -------------------------------------------------------
# Sample Plotter
# -------------------------------------------------------

from Tkinter import *
import os

class SimplePlot: 
    def __init__(self, robot, what):
        self.win = Tk()
        self.what = what
        self.robot = robot
        self.win.wm_title("pyro@%s: %s Sensors" % (os.getenv('HOSTNAME'),what))
        self.canvas = Canvas(self.win,width=400,height=120)
        self.canvas.pack()

        self.dataMin = 0
        self.dataMax = robot.get('range', 'maxvalue')
        self.dataWindowSize = 400
        self.dataSample = 1
        self.dataCount = 0
        self.lastRun = 0
        self.dataHist = [0] * self.robot.get('range', 'count')

    def redraw(self, options):
        # do something to draw yourself
        colors = ['blue', 'red', 'tan', 'yellow', 'orange', 'black', 'azure', 'beige', 'brown', 'coral', 'gold', 'ivory', 'moccasin', 'navy', 'salmon', 'tan', 'ivory']
        if self.dataCount > self.dataWindowSize:
            self.canvas.delete('data')
            self.dataCount = 0
        else:
            self.dataCount += 1
        for sensor in self.robot.sensorSet[self.what]:
            dist = self.robot.get('range', 'value', sensor)
            self.canvas.create_line(self.dataCount - 1,
                                    self.dataHist[sensor],
                                    self.dataCount,
                                    int(float(dist)/self.dataMax * 100.0),
                                    tags = 'data',
                                    width = 2,
                                    fill = colors[sensor])
            self.dataHist[sensor] = int(float(dist)/self.dataMax * 100.0 - 1)
