"""
A Pure Python 2D Robot Simulator
"""
import Tkinter, time, math
import pyrobot.system.share as share
from pyrobot.geometry import PIOVER180, Segment

class Simulator:
    def __init__(self):
        self.robots = []
        self.world = []
        self.time = 0.0
        self.robotConstructor = SimRobot

    def addWall(self, x1, y1, x2, y2):
        seg = Segment((x1, y1), (x2, y2))
        self.world.append(seg)
        seg.id = len(self.world)

    def addBox(self, ulx, uly, lrx, lry):
        self.addWall( ulx, uly, ulx, lry)
        self.addWall( ulx, uly, lrx, uly)
        self.addWall( ulx, lry, lrx, lry)
        self.addWall( lrx, uly, lrx, lry)

    def addRobot(self, name, x, y, a, geometry = None, color = "red"):
        r = self.robotConstructor(name, x, y, a, geometry, color)
        self.robots.append(r)
        r.simulator = self

    def scale_x(self, x): return 50 + (x * 20.0)
    def scale_y(self, y): return 700 - (y * 20.0)
        
    def step(self, timeslice = 100):
        """
        Advance the world by timeslice milliseconds.
        """
        # might want to randomize this order so the same ones
        # don't always move first:
        self.time += (timeslice / 1000.0)
        for r in self.robots:
            r.step(timeslice)
    def drawLine(self, x1, y1, x2, y2, color = None):
        pass
        
    def castRay(self, x1, y1, a, maxRange):
        hits = []
        x2, y2 = math.sin(a) * maxRange + x1, math.cos(a) * maxRange + y1
        seg = Segment((x1, y1), (x2, y2))
        # go down list of walls, and see if it hit anything:
        for w in self.world:
            retval = w.intersects(seg)
            if retval:
                dist = Segment(retval, (x1, y1)).length()
                if dist <= maxRange:
                    hits.append( (dist, retval, w.id) ) # distance, hit, id
        if len(hits) == 0:
            return (None, None, None)
        else:
            return min(hits)

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
        self.robotConstructor = TkSimRobot
        self.frame = Tkinter.Frame(self)
        self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                        fill = 'both')
        self.canvas = Tkinter.Canvas(self.frame, bg="white", width=600, height=600)
        self.canvas.pack(expand="yes", fill="both", side="top", anchor="n")
        #self.scrollbar = Tkinter.Scrollbar(self.frame, orient="h", command=self.scroll)
        #self.scrollbar.pack(expand="no", fill="x", side="bottom", anchor="s")
        self.after(100, self.step)
        
    def addWall(self, x1, y1, x2, y2):
        seg = Segment((x1, y1), (x2, y2))
        id = self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="line")
        seg.id = id
        self.world.append( seg )

    def drawLine(self, x1, y1, x2, y2, color):
        return self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="robot", fill=color)

    def step(self, timeslice = 100):
        self.canvas.delete('robot')
        Simulator.step(self, timeslice)
        self.after(100, self.step)

class SimRobot:
    def __init__(self, name, x, y, a, geometry = None, color = "red"):
        self.name = name
        self.x = x
        self.y = y
        self.a = a
        self.geometry = geometry
        self.color = color
        self.rangeDevices = []
        self.simulator = None # will be set when added to simulator
        self.vx, self.vy, self.va = (0.0, 0.0, 0.0) # meters / second, rads / second

    def step(self, timeslice = 100):
        """
        Move the robot self.velocity amount, if not blocked.
        """
        vy = self.vx * math.cos(-self.a) - self.vy * math.sin(-self.a)
        vx = self.vx * math.sin(-self.a) + self.vy * math.cos(-self.a)
        va = self.va
        self.x += vx * (timeslice / 1000.0) # miliseconds
        self.y += vy * (timeslice / 1000.0) # miliseconds
        self.a += va * (timeslice / 1000.0) # miliseconds
        for d in self.rangeDevices:
            d.scan = [0] * len(d.geometry)
            i = 0
            for x, y, a in d.geometry:
                ga = (self.a + a)
                a90 = self.a + 90 * PIOVER180
                gx = self.x + (x * math.cos(a90) - y * math.sin(a90))
                gy = self.y + (x * math.sin(a90) + y * math.cos(a90))
                dist, hit, id = self.simulator.castRay(gx, gy, -ga, d.maxRange)
                if hit:
                    self.simulator.drawLine(gx, gy, hit[0], hit[1], "gray")
                else:
                    hx, hy = math.sin(-ga) * d.maxRange, math.cos(-ga) * d.maxRange
                    dist = d.maxRange
                    self.simulator.drawLine(gx, gy, gx + hx, gy + hy, "gray")
                d.scan[i] = dist
                i += 1
        
    def addRanger(self, ranger):
        self.rangeDevices.append(ranger)

class Ranger:
    def __init__(self, name, geometry, arc, maxRange, noise = 0.0):
        self.name = name
        # geometry = (x, y, a) in meters and radians
        self.geometry = geometry
        self.arc = arc
        self.maxRange = maxRange
        self.noise = noise
        self.scan = [] # for data

class TkSimRobot(SimRobot):
    def step(self, timeslice = 100):
        SimRobot.step(self, timeslice)
        # FIX: Move it, rather than delete/recreate
        sx = [.15, .5, .5, .15, -.15, -.5, -.5, -.15]
        sy = [.75, .5, -.5, -.75, -.75, -.5, .5, .75]
        s_x = self.simulator.scale_x
        s_y = self.simulator.scale_y
        xy = map(lambda x, y: (s_x(self.x + x * math.cos(self.a) - y * math.sin(self.a)),
                               s_y(self.y + x * math.sin(self.a) + y * math.cos(self.a))),
                               sx, sy)
        self.simulator.canvas.create_polygon(xy, fill=self.color, tag="robot", outline="black")
        bx = [-.25, -.25, .25, .25]
        by = [ .5, .25, .25, .5]
        xy = map(lambda x, y: (s_x(self.x + x * math.cos(self.a) - y * math.sin(self.a)),
                               s_y(self.y + x * math.sin(self.a) + y * math.cos(self.a))),
                               bx, by)
        self.simulator.canvas.create_polygon(xy, tag="robot", fill="black")
        
if __name__ == "__main__":
    for constructor in [TkSimulator]: # [Simulator, TkSimulator]:
        sim = constructor()
        sim.addWall(5, 10, 15, 10)
        sim.addBox(5, 20, 45, 40)
        sim.addRobot("Test1", 10, 15, 0.0)
        sim.addRobot("Test2", 5, 15, 1.5, color="blue")
        sim.robots[0].addRanger(Ranger("sonar", geometry = (( 0.20, 0.50, 90 * PIOVER180),
                                                            ( 0.30, 0.40, 65 * PIOVER180),
                                                            ( 0.40, 0.30, 40 * PIOVER180),
                                                            ( 0.50, 0.20, 15 * PIOVER180),
                                                            ( 0.50,-0.20,-15 * PIOVER180),
                                                            ( 0.40,-0.30,-40 * PIOVER180),
                                                            ( 0.30,-0.40,-65 * PIOVER180),
                                                            ( 0.20,-0.50,-90 * PIOVER180),
                                                            
                                                            ),
                                       arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0))
        sim.mainloop()
