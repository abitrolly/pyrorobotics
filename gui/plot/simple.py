# -------------------------------------------------------
# Sample Plotter
# -------------------------------------------------------

import Tkinter
import random
from pyro.robot.device import Device

class SimplePlot(Device): 
    COLORS = ['blue', 'red', 'tan', 'yellow', 'orange', 'black',
              'azure', 'beige', 'brown', 'coral', 'gold', 'ivory',
              'moccasin', 'navy', 'salmon', 'tan', 'ivory']
    def __init__(self, robot, what, width = 400, height = 120):
        Device.__init__(self, "view", 0) # 1 = visible
        self.width = width
        self.height = height
        self.what = what
        self.robot = robot
        self.dataMin = 0
        self.dataMax = robot.get('robot', 'range', 'maxvalue')
        self.dataWindowSize = 400
        self.dataSample = 1
        self.dataCount = 0
        self.lastRun = 0
        self.dataHist = [0] * self.robot.get('robot', 'range', 'count')
        self.devData["source"] = self.what
        self.startDevice()
        self.makeWindow()
    def makeWindow(self):
        try:
            self.win.state()
            ok = 1
        except:
            ok = 0
        if ok:
            self.win.deiconify()
            self.setVisible(1)
        else:
            try:
                self.win = Tkinter.Toplevel()
            except:
                print "Pyro view cannot make window. Check DISPLAY variable."
                self.setVisible(0)
                return
            self.win.title("Pyro view: %s range sensors" % self.what)
            self.canvas = Tkinter.Canvas(self.win,width=self.width,height=self.height)
            self.canvas.pack()
            self.win.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
            self.setVisible(1)
    def hideWindow(self):
        self.setVisible(0)
        self.win.withdraw()
    def updateWindow(self, options = {}):
        # do something to draw yourself
        if self.dataCount > self.dataWindowSize:
            self.canvas.delete('data1')
            self.canvas.move("data2", -self.width/2, 0)
            self.canvas.itemconfigure("data2", tag = "data1")
            self.dataCount = self.dataWindowSize / 2
        else:
            self.dataCount += 1
        results = self.robot.get('robot', 'range', self.what, 'value,pos')
        for pair in results:
            dist = pair["value"]
            sensor = pair["pos"]
            if self.dataCount < self.dataWindowSize/2:
                tag = "data1"
            else:
                tag = "data2"
            self.canvas.create_line(self.dataCount - 1,
                                    self.dataHist[sensor],
                                    self.dataCount,
                                    int(float(dist)/self.dataMax * 100.0),
                                    tags = tag,
                                    width = 2,
                                    fill = SimplePlot.COLORS[sensor])
            self.dataHist[sensor] = int(float(dist)/self.dataMax * 100.0 - 1)
        self.win.update_idletasks()

if __name__ == '__main__':
    class Robot:
        def __init__(self):
            self.groups = {'all': (0,1)}
        def get(self, t1 = None, t2 = None, t3 = None):
            if t1 == "range" and t2 == "count":
                return 2
            elif t1 == "range" and t2 == "maxvalue":
                return 10.0
            else:
                return int(random.random() * 10)
    plot = SimplePlot(Robot(), 'all')
    for i in range(2500):
        plot.redraw()
    print "Done!"
    plot.mainloop()
