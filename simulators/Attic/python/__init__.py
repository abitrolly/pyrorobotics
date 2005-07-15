"""
A Pure Python 2D Robot Simulator
"""
from math import sin, cos
import Tkinter, time
import pyrobot.system.share as share

class Simulator:
    def __init__(self):
        self.objects = []
        self.world = []
        self.time = 0.0

    def addObject(self, obj):
        self.objects.append(obj)
        obj.simulator = self
        
    def step(self, timeslice = 100):
        """
        Advance the world by timeslice milliseconds.
        """
        # might want to randomize this order so the same ones
        # don't always move first:
        for obj in self.objects:
            obj.step(timeslice)
        self.time += (timeslice / 1000.0)
        self.updateWorld()

    def updateWorld(self):
        print "Time:", self.time
        for obj in self.objects:
            print obj.name, obj.x, obj.y, obj.thr
        

class TkSimulator(Simulator, Tkinter.Toplevel):
    def __init__(self, root = None):
        if root == None:
            if share.gui:
                root = share.gui
            else:
                root = Tkinter.Tk()
                root.withdraw()
        Tkinter.Toplevel.__init__(self, root)
        Simulator.__init__(self)
        self.frame = Tkinter.Frame(self)
        self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                        fill = 'both')
        self.canvas = Tkinter.Canvas(self.frame, bg="white")
        self.canvas.pack(expand="yes", fill="both", side="top", anchor="n")
        #self.scrollbar = Tkinter.Scrollbar(self.frame, orient="h", command=self.scroll)
        #self.scrollbar.pack(expand="no", fill="x", side="bottom", anchor="s")
        
    def updateWorld(self):
        print "Time:", self.time
        self.canvas.delete('all')
        for obj in self.objects:
            print obj.name, obj.x, obj.y, obj.thr
            self.canvas.create_oval(obj.x - 5, obj.y - 5,
                                    obj.x + 5, obj.y + 5)
        self.canvas.update()
        

class SimObject:
    def __init__(self, name, x, y, thr, geometry = None):
        self.name = name
        self.x = x
        self.y = y
        self.thr = thr
        self.geometry = geometry
        self.vx, self.vy = (1, 0.0) # meters / second

    def step(self, timeslice = 100):
        """
        Move the robot self.velocity amount, if not blocked.
        """
        vx = self.vx * cos(self.thr) - self.vy * sin(self.thr)
        vy = self.vx * sin(self.thr) + self.vy * cos(self.thr)
        self.x += vx * (timeslice / 1000.0) # miliseconds
        self.y += vy * (timeslice / 1000.0) # miliseconds
        # self.thr += vthr * (timeslice / 1000.0) # miliseconds

if __name__ == "__main__":
    print "Non-gui simulator:"
    sim = Simulator()
    sim.addObject(SimObject("Test1", 20, 20, 0.0))
    for i in range(10):
        sim.step()
    print "=" * 10
    print "Tk-gui simulator:"
    sim = TkSimulator()
    sim.addObject(SimObject("Test1", 20, 20, 0.0))
    for i in range(10):
        sim.step()
    sim.mainloop()
