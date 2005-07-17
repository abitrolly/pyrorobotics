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
        self.timeslice = 100
        self.scale = 10.0
        self.offset_x = 50.0
        self.offset_y = 700.0

    def addWall(self, x1, y1, x2, y2):
        seg = Segment((x1, y1), (x2, y2), len(self.world) + 1)
        self.world.append(seg)

    def addBox(self, ulx, uly, lrx, lry):
        self.addWall( ulx, uly, ulx, lry)
        self.addWall( ulx, uly, lrx, uly)
        self.addWall( ulx, lry, lrx, lry)
        self.addWall( lrx, uly, lrx, lry)

    def addRobot(self, name, x, y, a, geometry = None, color = "red"):
        r = self.robotConstructor(name, x, y, a, geometry, color)
        self.robots.append(r)
        r.simulator = self

    def scale_x(self, x): return self.offset_x + (x * self.scale)
    def scale_y(self, y): return self.offset_y - (y * self.scale)
        
    def step(self):
        """
        Advance the world by timeslice milliseconds.
        """
        # might want to randomize this order so the same ones
        # don't always move first:
        self.time += (self.timeslice / 1000.0)
        for r in self.robots:
            r.step(self.timeslice)
    def drawLine(self, x1, y1, x2, y2, color = None):
        pass
        
    def castRay(self, robot, x1, y1, a, maxRange):
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
        # go down list of robots, and see if you hit one:
        for r in self.robots:
            # but don't hit your own bounding box:
            if r.name == robot.name: continue
            a90 = r.a + 90 * PIOVER180
            xys = map(lambda x, y: (r.x + x * math.cos(a90) - y * math.sin(a90),
                                    r.y + x * math.sin(a90) + y * math.cos(a90)),
                      r.boundingBox[0], r.boundingBox[1])
            # for each of the bounding box segments:
            for i in range(len(xys)):
                w = Segment( xys[i], xys[i - 1])
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
        self.wm_title("Pyrobot Simulator")
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        Simulator.__init__(self)
        self.robotConstructor = TkSimRobot
        self.frame = Tkinter.Frame(self)
        self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                        fill = 'both')
        self.canvas = Tkinter.Canvas(self.frame, bg="white", width=600, height=600)
        self.canvas.pack(expand="yes", fill="both", side="top", anchor="n")
        self.canvas.bind("<ButtonRelease-1>", self.click_b1_up)
        self.canvas.bind("<ButtonRelease-3>", self.click_b3_up)
        self.canvas.bind("<Button-1>", self.click_b1_down)
        self.canvas.bind("<Button-3>", self.click_b3_down)
        self.canvas.bind("<B1-Motion>", self.click_b1_move)
        self.canvas.bind("<B3-Motion>", self.click_b3_move)
        self.after(100, self.step)

    def click_b1_down(self, event):
        self.click_start = event.x, event.y
    def click_b3_down(self, event):
        self.click_start = event.x, event.y
        self.click_b3_move(event)
    def click_b1_up(self, event):
        self.click_stop = event.x, event.y
        if self.click_stop == self.click_start:
            # center on this position:
            center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
            self.offset_x -= (self.click_stop[0] - center[0])
            self.offset_y -= (self.click_stop[1] - center[1])
        else: # move this much
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
            self.offset_x -= x_diff
            self.offset_y -= y_diff
        self.redraw()
    def click_b3_up(self, event):
        """
        Button handler for B3 for scaling window
        """
        stop = event.x, event.y
        center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        radius_stop = Segment(center, stop).length()
        radius_start = Segment(center, self.click_start).length()
        self.scale *= radius_stop/radius_start
        self.offset_x = (radius_stop/radius_start) * self.offset_x + (1 - (radius_stop/radius_start)) * center[0]
        self.offset_y = (radius_stop/radius_start) * self.offset_y + (1 - (radius_stop/radius_start)) * center[1]
        self.redraw()
    def click_b1_move(self, event):
        self.canvas.delete('arrow')
        self.click_stop = event.x, event.y
        x1, y1 = self.click_start
        x2, y2 = self.click_stop
        self.canvas.create_line(x1, y1, x2, y2, tag="arrow", fill="purple")
    def click_b3_move(self, event):
        self.canvas.delete('arrow')
        stop = event.x, event.y
        center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        radius = Segment(center, stop).length()
        self.canvas.create_oval(center[0] - radius, center[1] - radius,
                                center[0] + radius, center[1] + radius,
                                tag="arrow", outline="purple")
    def redraw(self):
        self.canvas.delete('all')
        for segment in self.world:
            (x1, y1), (x2, y2) = segment.start, segment.end
            id = self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="line")
            segment.id = id
        
    def addWall(self, x1, y1, x2, y2):
        seg = Segment((x1, y1), (x2, y2))
        id = self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="line")
        seg.id = id
        self.world.append( seg )

    def drawLine(self, x1, y1, x2, y2, color):
        return self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="robot", fill=color)

    def step(self):
        self.canvas.delete('robot')
        Simulator.step(self)
        self.after(self.timeslice, self.step)

class SimRobot:
    def __init__(self, name, x, y, a, geometry = None, color = "red"):
        self.name = name
        self.x = x
        self.y = y
        self.a = a
        self.boundingBox = geometry # ((x1, x2), (y1, y2)) of bounding box
        self.color = color
        self.rangeDevices = []
        self.simulator = None # will be set when added to simulator
        self.vx, self.vy, self.va = (0.0, 0.0, 0.0) # meters / second, rads / second
        self.display = {"body": 1, "boundingBox": 0, "rays": 1}
        self.stall = 0

    def updateDevices(self):
        # measure and draw the new range data:
        for d in self.rangeDevices:
            d.scan = [0] * len(d.geometry)
            i = 0
            for x, y, a in d.geometry:
                ga = (self.a + a)
                a90 = self.a + 90 * PIOVER180
                gx = self.x + (x * math.cos(a90) - y * math.sin(a90))
                gy = self.y + (x * math.sin(a90) + y * math.cos(a90))
                dist, hit, id = self.simulator.castRay(self, gx, gy, -ga, d.maxRange)
                if hit:
                    self.drawRay(gx, gy, hit[0], hit[1], "gray")
                else:
                    hx, hy = math.sin(-ga) * d.maxRange, math.cos(-ga) * d.maxRange
                    dist = d.maxRange
                    self.drawRay(gx, gy, gx + hx, gy + hy, "gray")
                d.scan[i] = dist
                i += 1

    def step(self, timeslice = 100):
        """
        Move the robot self.velocity amount, if not blocked.
        """
        vy = self.vx * math.cos(-self.a) - self.vy * math.sin(-self.a)
        vx = self.vx * math.sin(-self.a) + self.vy * math.cos(-self.a)
        va = self.va
        # proposed positions:
        p_x = self.x + vx * (timeslice / 1000.0) # miliseconds
        p_y = self.y + vy * (timeslice / 1000.0) # miliseconds
        p_a = self.a + va * (timeslice / 1000.0) # miliseconds
        # let's check if that movement would be ok:
        a90 = p_a + 90 * PIOVER180
        xys = map(lambda x, y: (p_x + x * math.cos(a90) - y * math.sin(a90),
                                p_y + x * math.sin(a90) + y * math.cos(a90)),
                  self.boundingBox[0], self.boundingBox[1])
        # for each of the robot's bounding box segments:
        for i in range(len(xys)):
            bb = Segment( xys[i], xys[i - 1])
            # check each segment of the robot's bounding box for wall obstacles:
            for w in self.simulator.world:
                if bb.intersects(w):
                    self.stall = 1
                    self.updateDevices()
                    return
            # check each segment of the robot's bounding box for other robots:
            for r in self.simulator.robots:
                if r.name == self.name: continue # don't compare with your own!
                r_a90 = r.a + 90 * PIOVER180
                r_xys = map(lambda x, y: (r.x + x * math.cos(r_a90) - y * math.sin(r_a90),
                                          r.y + x * math.sin(r_a90) + y * math.cos(r_a90)),
                            r.boundingBox[0], r.boundingBox[1])
                for j in range(len(r_xys)):
                    if bb.intersects(Segment(r_xys[j], r_xys[j - 1])):
                        self.stall = 1
                        self.updateDevices()
                        return
        # ok! move the robot
        self.stall = 0
        self.x = p_x
        self.y = p_y
        self.a = p_a
        self.updateDevices()
        
    def drawRay(self, x1, y1, x2, y2, color):
        pass
    
    def addRanger(self, ranger):
        self.rangeDevices.append(ranger)

class Ranger:
    def __init__(self, name, geometry, arc, maxRange, noise = 0.0):
        self.name = name
        # geometry = (x, y, a) origin in meters and radians
        self.geometry = geometry
        self.arc = arc
        self.maxRange = maxRange
        self.noise = noise
        self.scan = [] # for data

class TkSimRobot(SimRobot):
    def step(self, timeslice = 100):
        SimRobot.step(self, timeslice)
        # FIX: Move it, rather than delete/recreate
        sx = [.75, .5, -.5, -.75, -.75, -.5, .5, .75]
        sy = [.15, .5, .5, .15, -.15, -.5, -.5, -.15]
        s_x = self.simulator.scale_x
        s_y = self.simulator.scale_y
        a90 = self.a + 90 * PIOVER180 # angle is 90 degrees off for graphics
        if self.display["body"]:
            xy = map(lambda x, y: (s_x(self.x + x * math.cos(a90) - y * math.sin(a90)),
                                   s_y(self.y + x * math.sin(a90) + y * math.cos(a90))),
                     sx, sy)
            self.simulator.canvas.create_polygon(xy, fill=self.color, tag="robot", outline="black")
            bx = [ .5, .25, .25, .5] # front camera
            by = [-.25, -.25, .25, .25]
            xy = map(lambda x, y: (s_x(self.x + x * math.cos(a90) - y * math.sin(a90)),
                                   s_y(self.y + x * math.sin(a90) + y * math.cos(a90))),
                     bx, by)
            self.simulator.canvas.create_polygon(xy, tag="robot", fill="black")
        if self.display["boundingBox"]:
            xy = map(lambda x, y: (s_x(self.x + x * math.cos(a90) - y * math.sin(a90)),
                                   s_y(self.y + x * math.sin(a90) + y * math.cos(a90))),
                     self.boundingBox[0], self.boundingBox[1])
            self.simulator.canvas.create_polygon(xy, tag="robot", fill="", outline="purple")


    def drawRay(self, x1, y1, x2, y2, color):
        if self.display["rays"]:
            self.simulator.drawLine(x1, y1, x2, y2, "gray")
        
def run(constructor):
    """
    run() takes either TkSimulator or Simulator
    """
    sim = constructor()
    sim.addWall(5, 10, 15, 10)
    sim.addBox(5, 20, 45, 40)
    sim.addRobot("Test1", 10, 15, 0.0, ((.75, .75, -.75, -.75), (.5, -.5, -.5, .5)))
    sim.addRobot("Test2", 5, 15, 1.5, ((.75, .75, -.75, -.75), (.5, -.5, -.5, .5)), color="blue")
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
    sim.robots[1].addRanger(Ranger("sonar", geometry = (( 0.20, 0.50, 90 * PIOVER180),
                                                        ( 0.30, 0.40, 65 * PIOVER180),
                                                        ( 0.40, 0.30, 40 * PIOVER180),
                                                        ( 0.50, 0.20, 15 * PIOVER180),
                                                        ( 0.50,-0.20,-15 * PIOVER180),
                                                        ( 0.40,-0.30,-40 * PIOVER180),
                                                        ( 0.30,-0.40,-65 * PIOVER180),
                                                        ( 0.20,-0.50,-90 * PIOVER180),
                                                        
                                                        ),
                                   arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0))
    return sim

if __name__ == "__main__":
    sim = run(TkSimulator)
    sim.mainloop()
