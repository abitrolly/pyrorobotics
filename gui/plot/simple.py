# -------------------------------------------------------
# Sample Plotter
# -------------------------------------------------------

import Tkinter
import random

class SimplePlot(Tkinter.Tk): 
    COLORS = ['blue', 'red', 'tan', 'yellow', 'orange', 'black',
              'azure', 'beige', 'brown', 'coral', 'gold', 'ivory',
              'moccasin', 'navy', 'salmon', 'tan', 'ivory']
    def __init__(self, robot, what):
        Tkinter.Tk.__init__(self)
        self.what = what
        self.robot = robot
        self.title("%s Sensors" % what)
        self.canvas = Tkinter.Canvas(self,width=400,height=120)
        self.canvas.pack()
        self.dataMin = 0
        self.dataMax = robot.get('range', 'maxvalue')
        self.dataWindowSize = 400
        self.dataSample = 1
        self.dataCount = 0
        self.lastRun = 0
        self.dataHist = [0] * self.robot.get('range', 'count')
        self.update_idletasks()
        self.done = 0
        self.protocol('WM_DELETE_WINDOW',self.close)
    def close(self):
        self.done = 1
        self.withdraw()
        self.update_idletasks()
        self.destroy()
    def redraw(self, options = {}):
        # do something to draw yourself
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
                                    fill = SimplePlot.COLORS[sensor])
            self.dataHist[sensor] = int(float(dist)/self.dataMax * 100.0 - 1)
        self.update_idletasks()

if __name__ == '__main__':
    class Robot:
        def __init__(self):
            self.sensorSet = {'all': (0,1)}
        def get(self, t1 = None, t2 = None, t3 = None):
            return int(random.random() * 10)
    plot = SimplePlot(Robot(), 'all')
    plot.mainloop()
