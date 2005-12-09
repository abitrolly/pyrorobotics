"""
A Pure Python 2D Robot Simulator

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""
import Tkinter, time, math, pickle, random
import pyrobot.system.share as share
from pyrobot.geometry import PIOVER180, Segment

MAXRAYLENGTH = 1000.0 # some large measurement in meters
colorMap = {"red": (255, 0,0),
            "green": (0, 255,0),
            "blue": (0, 0,255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "cyan": (0, 255, 255),
            "yellow": (255, 255, 0),
            "brown": (165, 42, 42),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "violet": (238, 130, 238),
            "purple": (160, 32, 240),
            }

def sgn(v):
    if v >= 0: return +1
    else:      return -1

class Simulator:
    def __init__(self, (width, height), (offset_x, offset_y), scale):
        self.robots = []
        self.lights = []
        self.trail = []
        self.needToMove = [] # list of robots that need to move (see step)
        self.maxTrailSize = 5 * 60 * 10 # 5 minutes (one timeslice = 1/10 sec)
        self.trailStart = 0
        self.world = []
        self.time = 0.0
        self.timeslice = 100 # in milliseconds
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self._width, self._height = width, height
        self.lightAboveWalls = 0
        # connections to pyrobot:
        self.ports = []
        self.assoc = {}
        self.done = 0
        self.quit = 0
        self.properties = ["stall", "x", "y", "th", "thr", "energy"]
        self.supportedFeatures = ["range-sensor", "continuous-movement", "odometry"]
        self.stepCount = 0

    def addWall(self, x1, y1, x2, y2, color="black"):
        seg = Segment((x1, y1), (x2, y2), len(self.world) + 1)
        seg.color = color
        self.world.append(seg)

    def addBox(self, ulx, uly, lrx, lry, color="white", wallcolor="black"):
        self.addWall( ulx, uly, ulx, lry, wallcolor)
        self.addWall( ulx, uly, lrx, uly, wallcolor)
        self.addWall( ulx, lry, lrx, lry, wallcolor)
        self.addWall( lrx, uly, lrx, lry, wallcolor)

    def addLight(self, x, y, brightness, color="yellow"):
        self.lights.append(Light(x, y, brightness, color))
        self.redraw()

    def redraw(self): pass

    def addRobot(self, port, r):
        self.robots.append(r)
        self.trail.append([None] * self.maxTrailSize)
        r.simulator = self
        r._xya = r._gx, r._gy, r._ga # save original position for later reset
        if port != None:
            self.assoc[port] = r
            self.ports.append(port)

    def scale_x(self, x): return self.offset_x + (x * self.scale)
    def scale_y(self, y): return self.offset_y - (y * self.scale)

    def addTrail(self, pos, index, robot):
        self.trail[pos][index] = robot._gx, robot._gy, robot._ga
        
    def step(self):
        """
        Advance the world by timeslice milliseconds.
        """
        # might want to randomize this order so the same ones
        # don't always move first:
        self.needToMove = []
        self.time += (self.timeslice / 1000.0)
        i = 0
        for r in self.robots:
            r.step(self.timeslice)
            self.addTrail(i, self.stepCount % self.maxTrailSize, r)
            i += 1
        for r in self.needToMove:
            r.step(self.timeslice, movePucks = 0)
        if self.stepCount > self.maxTrailSize:
            self.trailStart = ((self.stepCount + 1) % self.maxTrailSize)
        self.stepCount += 1
    def drawLine(self, x1, y1, x2, y2, color = None):
        pass
        
    def castRay(self, robot, x1, y1, a, maxRange = MAXRAYLENGTH,
                ignoreRobot = "self",
                rayType = "range"):
        # ignoreRobot: all, self, other; 
        hits = []
        x2, y2 = math.sin(a) * maxRange + x1, math.cos(a) * maxRange + y1
        seg = Segment((x1, y1), (x2, y2))
        # go down list of walls, and see if it hit anything:
        # check if it is not a light ray, or if it is, and not above walls:
        if (rayType != "light") or (rayType == "light" and not self.lightAboveWalls):
            for w in self.world:
                retval = w.intersects(seg)
                if retval:
                    dist = Segment(retval, (x1, y1)).length()
                    if dist <= maxRange:
                        hits.append( (dist, retval, w) ) # distance, hit, obj
        # go down list of robots, and see if you hit one:
        if ignoreRobot != "all":
            for r in self.robots:
                # don't hit your own bounding box if ignoreRobot == "self":
                if r.name == robot.name and ignoreRobot == "self": continue
                # don't hit other's bounding box if ignoreRobot == "other":
                if r.name != robot.name and ignoreRobot == "other": continue
                a90 = r._ga + 90 * PIOVER180
                segments = []
                if r.boundingBox != []:
                    xys = map(lambda x, y: (r._gx + x * math.cos(a90) - y * math.sin(a90),
                                            r._gy + x * math.sin(a90) + y * math.cos(a90)),
                              r.boundingBox[0], r.boundingBox[1])
                    # for each of the bounding box segments:
                    for i in range(len(xys)):
                        w = Segment( xys[i], xys[i - 1]) # using the previous one completes the polygon
                        w.color = r.color
                        w.robot = r
                        segments.append(w)
                if r.boundingSeg != []:
                    # bounding segments
                    xys = map(lambda x, y: (r._gx + x * math.cos(a90) - y * math.sin(a90),
                                            r._gy + x * math.sin(a90) + y * math.cos(a90)),
                              r.boundingSeg[0], r.boundingSeg[1])
                    # for each of the bounding segments:
                    for i in range(0, len(xys), 2):
                        w = Segment( xys[i], xys[i + 1]) # assume that they come in pairs
                        w.color = r.color
                        w.robot = r
                        segments.append(w)
                for w in segments:
                    retval = w.intersects(seg)
                    if retval:
                        dist = Segment(retval, (x1, y1)).length()
                        if dist <= maxRange:
                            hits.append( (dist, retval, w) ) # distance,hit,obj
        if len(hits) == 0:
            return (None, None, None)
        else:
            return min(hits)

    def process(self, request, sockname):
        """
        Process does all of the work.
        request  - a string message
        sockname - (IPNUMBER (str), SOCKETNUM (int)) from client
        """
        retval = 'error'
        if request == 'reset':
            self.reset()
            retval = "ok"
        elif request.count('connectionNum'):
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )
        elif request == 'end' or request == 'exit':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        elif request == "disconnect":
            retval = "ok"
        elif request == 'properties':
            retval = self.properties
        elif request == 'supportedFeatures':
            retval = self.supportedFeatures
        elif request == 'builtinDevices':
            retval = self.assoc[sockname[1]].builtinDevices
        elif request == 'forward':
            self.assoc[sockname[1]].move(0.3, 0.0)
            retval = "ok"
        elif request == 'left':
            self.assoc[sockname[1]].move(0.0, 0.3)
            retval = "ok"
        elif request == 'right':
            self.assoc[sockname[1]].move(0.0, -0.3)
            retval = "ok"
        elif request == 'back':
            self.assoc[sockname[1]].move(-0.3, 0.0)
            retval = "ok"
        elif request == 'name':
            retval = self.assoc[sockname[1]].name
        elif request == 'x':
            retval = self.assoc[sockname[1]].x
        elif request == 'energy':
            retval = self.assoc[sockname[1]].energy
        elif request == 'y':
            retval = self.assoc[sockname[1]].y
        elif request == 'stall':
            retval = self.assoc[sockname[1]].stall
        elif request == 'radius':
            retval = self.assoc[sockname[1]].radius
        elif request == 'thr':
            retval = self.assoc[sockname[1]].a
        elif request == 'th':
            retval = self.assoc[sockname[1]].a / PIOVER180
        elif len(request) > 1 and request[0] == '!': # eval
            try:
                retval = eval(request[1:])
            except:
                try:
                    exec request[1:]
                    retval = "ok"
                except:
                    retval = "error"
        else:
            # assume a package
            message = request.split("_")
            if message[0] == "m": # "m_t_r" move:translate:rotate
                retval = self.assoc[sockname[1]].move(float(message[1]), float(message[2]))
            elif message[0] == "a": # "a_name_x_y_th" simulation placement
                simulation, name, x, y, thr = message
                for r in self.robots:
                    if r.name == name:
                        r.setPose(float(x), float(y), float(thr), 1)#handofgod
                        r.localize(0, 0, 0)
                        return "ok"
                return "error"
            elif message[0] == "b": # "b_x_y_th" localize
                localization, x, y, thr = message
                retval = self.assoc[sockname[1]].localize(float(x), float(y), float(thr))
            elif message[0] == "c": # "c_name" getpose
                simulation, name = message
                retval = "error"
                for r in self.robots:
                    if r.name == name:
                        retval = (r._gx, r._gy, r._ga)
            elif message[0] == "f": # "f_i_v" rgb[i][v]
                index, pos = int(message[1]), int(message[2])
                device = self.assoc[sockname[1]].getIndex("light", index)
                if device:
                    retval = device.rgb[pos]
            elif message[0] == "h": # "h_v" bulb:value
                self.assoc[sockname[1]].bulb.brightness = float(message[1])
                self.redraw()
                return "ok"
            elif message[0] == "t": # "t_v" translate:value
                retval = self.assoc[sockname[1]].translate(float(message[1]))
            elif message[0] == "v": # "v_v" global step scalar:value
                self.assoc[sockname[1]].stepScalar = float(message[1])
                retval = "ok"
            elif message[0] == "o": # "o_v" rotate:value
                retval = self.assoc[sockname[1]].rotate(float(message[1]))
            elif message[0] == "d": # "d_sonar" display:keyword
                retval = self.assoc[sockname[1]].display[message[1]] = 1
            elif message[0] == "e": # "e_amt" eat:keyword
                retval = self.assoc[sockname[1]].eat(float(message[1]))
            elif message[0] == "x": # "x_expression" expression
                retval = eval(message[1])
            elif message[0] == "z": # "z_gripper_0_command" command
                type = message[1]
                index = int(message[2])
                command = message[3]
                device = self.assoc[sockname[1]].getIndex(type, index)
                if device:
                    retval = device.__class__.__dict__[command](device)
            elif message[0] == "g": # "g_sonar_0" geometry_sensor_id
                index = 0
                for d in self.assoc[sockname[1]].devices:
                    if d.type == message[1]:
                        if int(message[2]) == index:
                            if message[1] in ["sonar", "laser", "light", "bulb"]:
                                retval = d.geometry, d.arc, d.maxRange
                            elif message[1] == "camera":
                                retval = d.width, d.height
                        index += 1
            elif message[0] == "r": # "r_sonar_0" groups_sensor_id
                index = 0
                for d in self.assoc[sockname[1]].devices:
                    if d.type == message[1]:
                        if int(message[2]) == index:
                            if message[1] in ["sonar", "laser", "light"]:
                                retval = d.groups
                        index += 1
            elif message[0] == "s": # "s_sonar_0" subscribe
                if message[1] in self.assoc[sockname[1]].display and self.assoc[sockname[1]].display[message[1]] != -1:
                    self.assoc[sockname[1]].display[message[1]] = 1
                self.properties.append("%s_%s" % (message[1], message[2]))
                self.assoc[sockname[1]].subscribed = 1
                retval = "ok"
            elif message[0] in ["sonar", "laser", "light", "camera", "gripper"]: # sonar_0, light_0...
                index = 0
                for d in self.assoc[sockname[1]].devices:
                    if d.type == message[0]:
                        try:    i = int(message[1])
                        except: i = -1
                        if i == index:
                            retval = d.scan
                        index += 1
        return pickle.dumps(retval)

class TkSimulator(Simulator, Tkinter.Toplevel):
    def __init__(self, offset_x, offset_y, scale, root = None):
        if root == None:
            if share.gui:
                root = share.gui
            else:
                root = Tkinter.Tk()
                root.withdraw()
        Tkinter.Toplevel.__init__(self, root)
        Simulator.__init__(self, offset_x, offset_y, scale)
        self.root = root
        self.wm_title("Pyrobot Simulator")
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.frame = Tkinter.Frame(self)
        self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                        fill = 'both')
        self.canvas = Tkinter.Canvas(self.frame, bg="white", width=self._width, height=self._height)
        self.canvas.pack(expand="yes", fill="both", side="top", anchor="n")
        self.canvas.bind("<ButtonRelease-2>", self.click_b2_up)
        self.canvas.bind("<ButtonRelease-3>", self.click_b3_up)
        self.canvas.bind("<Button-2>", self.click_b2_down)
        self.canvas.bind("<Button-3>", self.click_b3_down)
        self.canvas.bind("<B2-Motion>", self.click_b2_move)
        self.canvas.bind("<B3-Motion>", self.click_b3_move)
        self.mBar = Tkinter.Frame(self, relief=Tkinter.RAISED, borderwidth=2)
        self.mBar.pack(fill=Tkinter.X)
        self.menuButtons = {}
        menu = [
            ('File', [['Reset', self.reset],
                      ['Exit', self.destroy]]),
            ('View',[
            ['trail', lambda: self.toggle("trail")],                     
            ['body', lambda: self.toggle("body")],                 
            ['boundingBox', lambda: self.toggle("boundingBox")],
            ['gripper', lambda: self.toggle("gripper")],
            ['camera', lambda: self.toggle("camera")],
            ['sonar', lambda: self.toggle("sonar")],
            ['light', lambda: self.toggle("light")],                     
            ['lightBlocked', lambda: self.toggle("lightBlocked")], 
            ]
             ),
            ('Options', [['lights visible above walls',
                          lambda: self.toggleOption("lightAboveWalls")]]),
            ]
        for entry in menu:
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))
        self.shapes = []
        self.after(100, self.step)
    def toggleOption(self, key):
        if key == "lightAboveWalls":
            self.lightAboveWalls = not self.lightAboveWalls
        else:
            raise AttributeError, "invalid key: '%s'" % key
        self.redraw()
    def toggle(self, key):
        for r in self.robots:
            if r.subscribed == 0: continue
            if r.display[key] == 1:
                r.display[key] = 0
            else:
                r.display[key] = 1
            r._last_pose = (-1, -1, -1)
        self.redraw()
    def reset(self):
        for r in self.robots:
            r._gx, r._gy, r._ga = r._xya
            r.energy = 10000.0
        for l in self.lights:
            l.x, l.y, l.brightness = l._xyb
        self.redraw()
    def makeMenu(self, bar, name, commands):
        """ Assumes self.menuButtons exists """
        menu = Tkinter.Menubutton(bar,text=name,underline=0)
        self.menuButtons[name] = menu
        menu.pack(side=Tkinter.LEFT,padx="2m")
        menu.filemenu = Tkinter.Menu(menu)
        for cmd in commands:
            if cmd:
                menu.filemenu.add_command(label=cmd[0],command=cmd[1])
            else:
                menu.filemenu.add_separator()
        menu['menu'] = menu.filemenu
        return menu
    def destroy(self):
        self.done = 1 # stop processing requests, if handling
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui
    def click_b2_down(self, event):
        self.click_start = event.x, event.y
    def click_b3_down(self, event):
        self.click_start = event.x, event.y
        self.click_b3_move(event)
    def click_b2_up(self, event):
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
    def click_b2_move(self, event):
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
        print "Window: size=(%d,%d), offset=(%d,%d), scale=%f" % (self.winfo_width(), self.winfo_height(),
                                                                  self.offset_x, self.offset_y, self.scale)
        self.canvas.delete('all')
        for shape in self.shapes:
            if shape[0] == "box":
                name, ulx, uly, lrx, lry, color = shape
                self.canvas.create_rectangle(self.scale_x(ulx), self.scale_y(uly),
                                             self.scale_x(lrx), self.scale_y(lry),
                                             tag="line", fill=color, outline="black")
        for segment in self.world:
            (x1, y1), (x2, y2) = segment.start, segment.end
            id = self.canvas.create_line(self.scale_x(x1), self.scale_y(y1),
                                         self.scale_x(x2), self.scale_y(y2),
                                         tag="line")
            segment.id = id
        for light in self.lights:
            if light.type != "fixed": continue 
            x, y, brightness, color = light.x, light.y, light.brightness, light.color
            self.canvas.create_oval(self.scale_x(x - brightness), self.scale_y(y - brightness),
                                    self.scale_x(x + brightness), self.scale_y(y + brightness),
                                    tag="line", fill=color, outline="orange")
        i = 0
        for path in self.trail:
            if self.robots[i].subscribed and self.robots[i].display["trail"] == 1:
                if path[self.trailStart] != None:
                    lastX, lastY, lastA = path[self.trailStart]
                    lastX, lastY = self.scale_x(lastX), self.scale_y(lastY)
                    color = self.robots[i].color
                    for p in range(self.trailStart, self.trailStart + self.maxTrailSize):
                        xya = path[p % self.maxTrailSize]
                        if xya == None: break
                        x, y = self.scale_x(xya[0]), self.scale_y(xya[1])
                        self.canvas.create_line(lastX, lastY, x, y, fill=color)
                        lastX, lastY = x, y
            i += 1
        for robot in self.robots:
            robot._last_pose = (-1, -1, -1)
            print "   %s: pose = (%.2f, %.2f, %.2f)" % (robot.name, robot._gx, robot._gy, robot._ga % (2 * math.pi))
        
    def addBox(self, ulx, uly, lrx, lry, color="white", wallcolor="black"):
        Simulator.addBox(self, ulx, uly, lrx, lry, color, wallcolor)
        self.shapes.append( ("box", ulx, uly, lrx, lry, color) )
        self.redraw()
    def addWall(self, x1, y1, x2, y2, color="black"):
        seg = Segment((x1, y1), (x2, y2))
        seg.color = color
        id = self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="line")
        seg.id = id
        self.world.append( seg )

    def drawLine(self, x1, y1, x2, y2, color):
        return self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag="robot", fill=color)

    def step(self):
        self.canvas.delete('robot')
        Simulator.step(self)
        self.after(self.timeslice, self.step)

    def addTrail(self, pos, index, robot):
        Simulator.addTrail(self, pos, index, robot)
        if robot.display["trail"] == 1:
            xya = self.trail[pos][(index - 1) % self.maxTrailSize]
            if xya != None:
                x1, y1 = self.scale_x(xya[0]), self.scale_y(xya[1])
                x2, y2 = self.scale_x(robot._gx), self.scale_y(robot._gy)
                self.canvas.create_line(x1, y1, x2, y2, fill=robot.color)

class SimRobot:
    def __init__(self, name, x, y, a, boundingBox = [], color = "red"):
        if " " in name:
            name = name.replace(" ", "_")
        self.name = name
        self.type = "robot"
        # set them here manually: (afterwards, use setPose)
        self.stepScalar = 1.0 # normally = 1.0
        self._gx = x
        self._gy = y
        self._ga = a
        self.subscribed = 0
        self.x, self.y, self.a = (0.0, 0.0, 0.0) # localize
        self.boundingBox = boundingBox # ((x1, x2), (y1, y2)) NOTE: Xs then Ys of bounding box
        self.boundingSeg = []
        if boundingBox != []:
            self.radius = max(max(map(abs, boundingBox[0])), max(map(abs, boundingBox[1]))) # meters
        else:
            self.radius = 0.0
        self.builtinDevices = []
        self.color = color
        self.devices = []
        self.simulator = None # will be set when added to simulator
        self.vx, self.vy, self.va = (0.0, 0.0, 0.0) # meters / second, rads / second
        self.friction = 1.0
        # -1: don't automatically turn display on when subscribing:
        self.display = {"body": 1, "boundingBox": 0, "gripper": -1, "camera": 0, "sonar": 0,
                        "light": -1, "lightBlocked": 0, "trail": -1} 
        self.stall = 0
        self.energy = 10000.0
        self.maxEnergyCostPerStep = 1.0
        # FIXME
        #self.noiseTranslate = 0.01 # percent of translational noise 
        #self.noiseRotate    = 0.01 # percent of translational noise 
        self._mouse = 0 # mouse down?
        self._mouse_xy = (0, 0) # last mouse click
        self._last_pose = (-1, -1, -1) # last robot pose drawn

    def addBoundingSeg(self, boundingSeg):
        if self.boundingSeg == []:
            self.boundingSeg = boundingSeg
        else:
            self.boundingSeg[0].extend(boundingSeg[0])
            self.boundingSeg[1].extend(boundingSeg[1])
        segradius = max(max(map(abs, boundingSeg[0])), max(map(abs, boundingSeg[1]))) # meters
        self.radius = max(self.radius, segradius)
        
    def localize(self, x = 0, y = 0, th = 0):
        self.x, self.y, self.a = (x, y, th)

    def setPose(self, x = None, y = None, a = None, handOfGod = 0):
        if x != None: # we never send just x; always comes with y
            if self._mouse != 1 and not handOfGod: # if the mouse isn't down:
                # first, figure out how much we moved in the global coords:
                a90 = -self._ga
                dx =  (x - self._gx) * math.cos(a90) - (y - self._gy) * math.sin(a90)
                dy =  (x - self._gx) * math.sin(a90) + (y - self._gy) * math.cos(a90)
                # then, move that much in the local coords:
                a90 = -self.a
                self.y += dx * math.cos(a90) - dy * math.sin(a90) 
                self.x += dx * math.sin(a90) + dy * math.cos(a90) 
                # noise: --------------------------------------------------------------
                # FIXME: should be based on the total distance moved:
                # dist = Segment((x, y), (self._gx, self._gy)).length()
                # but distributed over x and y components, gaussian?
                # Velocity should maybe play a role, too
            # just update the global position
            self._gx = x
            self._gy = y
        if a != None:
            # if our angle changes, update localized position:
            if self._mouse != 1 and not handOfGod: # if mouse isn't down
                diff = a - self._ga
                self.a += diff 
                self.a = self.a % (2 * math.pi) # keep in the positive range
            # just update the global position
            self._ga = a % (2 * math.pi) # keep in the positive range
            # noise: --------------------------------------------------------------
            # FIXME: add gaussian(noiseRotate)
    def move(self, vx, va):
        self.vx = vx
        self.va = va
        return "ok"

    def rotate(self, va):
        self.va = va
        return "ok"

    def translate(self, vx):
        self.vx = vx
        return "ok"

    def getIndex(self, dtype, i):
        index = 0
        for d in self.devices:
            if d.type == dtype:
                if i == index:
                    return d
                index += 1
        return None

    def updateDevices(self):
        # measure and draw the new device data:
        if self.subscribed == 0: return
        for d in self.devices:
            if d.type == "sonar":
                i = 0
                for x, y, a in d.geometry:
                    ga = (self._ga + a)
                    a90 = self._ga + 90 * PIOVER180
                    gx = self._gx + (x * math.cos(a90) - y * math.sin(a90))
                    gy = self._gy + (x * math.sin(a90) + y * math.cos(a90))
                    dist, hit, obj = self.simulator.castRay(self, gx, gy, -ga, d.maxRange)
                    if hit:
                        self.drawRay("sonar", gx, gy, hit[0], hit[1], "gray")
                    else:
                        hx, hy = math.sin(-ga) * d.maxRange, math.cos(-ga) * d.maxRange
                        dist = d.maxRange
                        self.drawRay("sonar", gx, gy, gx + hx, gy + hy, "gray")
                    d.scan[i] = dist
                    i += 1
            elif d.type == "bulb":
                pass # nothing to update... it is not a sensor
            elif d.type == "light":
                # for each light sensor:
                i = 0
                for (d_x, d_y, d_a) in d.geometry:
                    # compute total light on sensor, falling off as square of distance
                    # position of light sensor in global coords:
                    a90 = self._ga + 90 * PIOVER180
                    gx = self._gx + (d_x * math.cos(a90) - d_y * math.sin(a90))
                    gy = self._gy + (d_x * math.sin(a90) + d_y * math.cos(a90))
                    sum = 0.0
                    rgb = [0, 0, 0]
                    for light in self.simulator.lights: # for each light source:
                        # these can be type == "fixed" and type == "bulb"
                        if light.type == "fixed": 
                            x, y, brightness, light_rgb = light.x, light.y, light.brightness, light.rgb
                        else: # get position from robot:
                            if light.robot == self: continue # don't read the bulb if it is on self
                            ogx, ogy, oga, brightness, color = (light.robot._gx,
                                                                light.robot._gy,
                                                                light.robot._ga,
                                                                light.brightness, light.robot.color)
                            oa90 = oga + 90 * PIOVER180
                            x = ogx + (light.x * math.cos(oa90) - light.y * math.sin(oa90))
                            y = ogy + (light.x * math.sin(oa90) + light.y * math.cos(oa90))
                            light_rgb = colorMap[color]
                        seg = Segment((x,y), (gx, gy))
                        a = -seg.angle() + 90 * PIOVER180
                        # see if line between sensor and light is blocked by any boundaries (ignore other bb)
                        dist,hit,obj = self.simulator.castRay(self, x, y, a, seg.length() - .1,
                                                               ignoreRobot = "other", rayType = "light")
                        # compute distance of segment; value is sqrt of that?
                        if not hit: # no hit means it has a clear shot:
                            self.drawRay("light", x, y, gx, gy, "orange")
                            intensity = (1.0 / (seg.length() * seg.length())) 
                            sum += intensity * brightness * 1000.0
                            for c in [0, 1, 2]:
                                rgb[c] += light_rgb[c] * (1.0/ seg.length())
                        else:
                            self.drawRay("lightBlocked", x, y, hit[0], hit[1], "purple")
                    d.scan[i] = min(sum, d.maxRange)
                    for c in [0, 1, 2]:
                        d.rgb[i][c] = min(int(rgb[c]), 255)
                    i += 1
            elif d.type == "gripper":
                # cast a ray in two places, set scan = 1 if it is "broken"
                a90 = self._ga + 90 * PIOVER180
                # FIX: make this based on gripper details:
                x = 0.3
                y = 0.12
                d.scan = [0] * 2
                d.objs = []
                for i in range(2):
                    gx = self._gx + (x * math.cos(a90) - y * math.sin(a90))
                    gy = self._gy + (x * math.sin(a90) + y * math.cos(a90))
                    ogx = self._gx + (x * math.cos(a90) + y * math.sin(a90))
                    ogy = self._gy + (x * math.sin(a90) - y * math.cos(a90))
                    dist,hit,obj = self.simulator.castRay(self, gx, gy, -self._ga + (90 * PIOVER180), 2 * y,
                                                          rayType = "breakBeam")
                    if hit: 
                        d.scan[i] = 1
                        d.objs.append(obj) # for gripping
                        if self.display["gripper"] == 1:
                            self.drawRay("gripper", gx, gy, ogx, ogy, "orange")
                    elif self.display["gripper"] == 1:
                        self.drawRay("gripper", gx, gy, ogx, ogy, "purple")
                    x += .07
            elif d.type == "camera":
                # FIX: make work with any start/stop angle:
                x, y = self._gx, self._gy
                stepAngle = (abs(d.startAngle) + abs(d.stopAngle)) / float(d.width - 1)
                a = d.startAngle
                d.scan = []
                for i in range(d.width):
                    # FIX: move camera to d.pose; currently assumes robot center
                    ga = (self._ga + a) 
                    dist,hit,obj = self.simulator.castRay(self, x, y, -ga,
                                                           ignoreRobot="self",
                                                           rayType = "camera")
                    if obj != None:
                        if i in [0, d.width - 1]:
                            self.drawRay("camera", x, y, hit[0], hit[1], "purple")
                        d.scan.append((obj.color, dist))
                    else:
                        d.scan.append((None, None))
                    a -= stepAngle
            else:
                raise AttributeError, "unknown type of device: '%s'" % d.type

    def eat(self, amt):
        for light in self.simulator.lights:
            if light != "fixed": continue
            dist = Segment((self._gx, self._gy), (light.x, light.y)).length()
            radius = max(light.brightness, self.radius)
            if dist <= radius and amt/1000.0 <= light.brightness:
                light.brightness -= amt/1000.0
                self.energy += amt
                self.simulator.redraw()
                return amt
        return 0.0

    def step(self, timeslice = 100, movePucks = 1):
        """
        Move the robot self.velocity amount, if not blocked.
        """
        if self._mouse: return # don't do any of this if mouse is down
        gvx = self.vx * self.stepScalar
        gvy = self.vy * self.stepScalar
        vx = gvx * math.sin(-self._ga) + gvy * math.cos(-self._ga)
        vy = gvx * math.cos(-self._ga) - gvy * math.sin(-self._ga)
        va = self.va
        # proposed positions:
        p_x = self._gx + vx * (timeslice / 1000.0) # miliseconds
        p_y = self._gy + vy * (timeslice / 1000.0) # miliseconds
        p_a = self._ga + va * (timeslice / 1000.0) # miliseconds
        pushedAPuck = 0
        # for each of the robot's bounding box segments:
        if self.subscribed or self.type == "puck":
            if vx != 0 or vy != 0 or va != 0:
                self.energy -= self.maxEnergyCostPerStep
            # let's check if that movement would be ok:
            a90 = p_a + 90 * PIOVER180
            segments = []
            if self.boundingBox != []:
                xys = map(lambda x, y: (p_x + x * math.cos(a90) - y * math.sin(a90),
                                        p_y + x * math.sin(a90) + y * math.cos(a90)),
                          self.boundingBox[0], self.boundingBox[1])
                for i in range(len(xys)):
                    bb = Segment( xys[i], xys[i - 1])
                    segments.append(bb)
            if self.boundingSeg != []:
                xys = map(lambda x, y: (p_x + x * math.cos(a90) - y * math.sin(a90),
                                        p_y + x * math.sin(a90) + y * math.cos(a90)),
                          self.boundingSeg[0], self.boundingSeg[1])
                for i in range(0, len(xys), 2):
                    bb = Segment( xys[i], xys[i + 1])
                    segments.append(bb)
            for bb in segments:
                # check each segment of the robot's bounding segs for wall obstacles:
                for w in self.simulator.world:
                    if bb.intersects(w):
                        self.stall = 1
                        self.updateDevices()
                        self.draw()
                        return
                # check each segment of the robot's bounding box for other robots:
                for r in self.simulator.robots:
                    if r.name == self.name: continue # don't compare with your own!
                    r_a90 = r._ga + 90 * PIOVER180
                    r_segments = []
                    if r.boundingBox != []:
                        r_xys = map(lambda x, y: (r._gx + x * math.cos(r_a90) - y * math.sin(r_a90),
                                                  r._gy + x * math.sin(r_a90) + y * math.cos(r_a90)),
                                    r.boundingBox[0], r.boundingBox[1])
                        for j in range(len(r_xys)):
                            r_seg = Segment(r_xys[j], r_xys[j - 1])
                            r_segments.append(r_seg)
                    if r.boundingSeg != []:
                        r_xys = map(lambda x, y: (r._gx + x * math.cos(r_a90) - y * math.sin(r_a90),
                                                  r._gy + x * math.sin(r_a90) + y * math.cos(r_a90)),
                                    r.boundingSeg[0], r.boundingSeg[1])
                        for j in range(0, len(r_xys), 2):
                            r_seg = Segment(r_xys[j], r_xys[j + 1])
                            r_segments.append(r_seg)
                    for r_seg in r_segments:
                        bbintersect = bb.intersects(r_seg)
                        if r.type == "puck": # other robot is a puck
                            if bbintersect:
                                # transfer some energy to puck
                                if movePucks:
                                    r._ga = self._ga + ((random.random() - .5) * 0.4) # send in random direction, 22 degree
                                    r.vx = self.vx * 0.9 # knock it away
                                    if r not in self.simulator.needToMove:
                                        self.simulator.needToMove.append(r)
                                    if self.type == "puck":
                                        self.vx = self.vx * 0.9 # loose some
                                pushedAPuck = 1
                        elif bbintersect:
                            if self.type == "puck":
                                self.vx = 0.0
                                self.vy = 0.0
                            self.stall = 1
                            self.updateDevices()
                            self.draw()
                            return
        if pushedAPuck:
            if movePucks and r not in self.simulator.needToMove:
                self.simulator.needToMove.append( self )
            else:
                self.stall = 1
                self.updateDevices()
                self.draw()
            return
        # ok! move the robot, if it wanted to move
        if self.friction != 1.0:
            self.vx *= self.friction
            self.vy *= self.friction
            if 0.0 < self.vx < 0.1: self.vx = 0.0
            if 0.0 < self.vy < 0.1: self.vy = 0.0
            if 0.0 > self.vx > -0.1: self.vx = 0.0
            if 0.0 > self.vy > -0.1: self.vy = 0.0
        self.stall = 0
        self.setPose(p_x, p_y, p_a)
        self.updateDevices()
        self.draw()
    def draw(self): pass
    def drawRay(self, type, x1, y1, x2, y2, color):
        if self.display[type] == 1:
            self.simulator.drawLine(x1, y1, x2, y2, color)
    def addDevice(self, dev):
        self.devices.append(dev)
        if dev.type not in self.builtinDevices:
            self.builtinDevices.append(dev.type)
        if dev.type == "bulb":
            self.simulator.lights.append( dev )
            dev.robot = self
            self.bulb = dev
        elif dev.type == "camera":
            dev.robot = self
        elif dev.type == "gripper":
            dev.robot = self
            self.gripper = dev
            dev.robot.addBoundingSeg(dev.boundingSeg)

class TkRobot(SimRobot):
    def __init__(self, *args, **kwargs):
        SimRobot.__init__(self, *args, **kwargs)
        self.bulb = None
        self.gripper = None
    def mouse_event(self, event, command, robot):
        x, y = event.x, event.y
        if command[:8] == "control-":
            self._mouse_xy = x, y
            cx, cy = self.simulator.scale_x(robot._gx), self.simulator.scale_y(robot._gy)
            if command == "control-up":
                self.simulator.canvas.delete('arrow')
                a = Segment((cx, cy), (x, y)).angle()
                robot.setPose(a = (-a - 90 * PIOVER180) % (2 * math.pi))
                self._mouse = 0
                self.simulator.redraw()
            elif command in ["control-down", "control-motion"]:
                self._mouse = 1
                self.simulator.canvas.delete('arrow')
                self.simulator.canvas.create_line(cx, cy, x, y, tag="arrow", fill="purple")
        else:
            if command == "up":
                x -= self.simulator.offset_x
                y -= self.simulator.offset_y
                x, y = map(lambda v: float(v) / self.simulator.scale, (x, -y))
                robot.setPose(x - self._mouse_offset_from_center[0],
                              y - self._mouse_offset_from_center[1])
                self._mouse = 0
                self.simulator.redraw()
            elif command == "down":
                self._mouse = 1
                self._mouse_xy = x, y
                cx = x - self.simulator.offset_x
                cy = y - self.simulator.offset_y
                cx, cy = map(lambda v: float(v) / self.simulator.scale, (cx, -cy))
                self._mouse_offset_from_center = cx - self._gx, cy - self._gy
                self.simulator.canvas.move("robot-%s" % robot.name, x - self._mouse_xy[0], y - self._mouse_xy[1])
            elif command == "motion":
                self._mouse = 1
                self.simulator.canvas.move("robot-%s" % robot.name, x - self._mouse_xy[0], y - self._mouse_xy[1])
                self._mouse_xy = x, y
                # now move it so others will see it it correct place as you drag it:
                x -= self.simulator.offset_x
                y -= self.simulator.offset_y
                x, y = map(lambda v: float(v) / self.simulator.scale, (x, -y))
                robot.setPose(x, y)
        return "break"
    def addMouseBindings(self):
        ### Mouse methods:
        self.simulator.canvas.tag_bind("robot-%s" % self.name, "<B1-Motion>",
                                       func=lambda event,robot=self:self.mouse_event(event, "motion", robot))
        self.simulator.canvas.tag_bind("robot-%s" % self.name, "<Button-1>",
                                       func=lambda event,robot=self:self.mouse_event(event, "down", robot))
        self.simulator.canvas.tag_bind("robot-%s" % self.name, "<ButtonRelease-1>",
                                       func=lambda event,robot=self:self.mouse_event(event, "up", robot))
        self.simulator.canvas.tag_bind("robot-%s" % self.name, "<Control-B1-Motion>",
                                       func=lambda event,robot=self:self.mouse_event(event, "control-motion", robot))
        self.simulator.canvas.tag_bind("robot-%s" % self.name, "<Control-Button-1>",
                                       func=lambda event,robot=self:self.mouse_event(event, "control-down", robot))
        self.simulator.canvas.tag_bind("robot-%s" % self.name, "<Control-ButtonRelease-1>",
                                       func=lambda event,robot=self:self.mouse_event(event, "control-up", robot))

class Puck(SimRobot):
    def __init__(self, *args, **kwargs):
        SimRobot.__init__(self, *args, **kwargs)
        self.radius = 0.05
        self.friction = 0.90
        self.type = "puck"

class TkPuck(TkRobot):
    def __init__(self, *args, **kwargs):
        TkRobot.__init__(self, *args, **kwargs)
        self.radius = 0.05
        self.friction = 0.90
        self.type = "puck"
    def draw(self):
        """
        Draws the body of the robot. Not very efficient.
        """
        if  self._last_pose == (self._gx, self._gy, self._ga): return # hasn't moved
        self._last_pose = (self._gx, self._gy, self._ga)
        self.simulator.canvas.delete("robot-%s" % self.name)
        s_x = self.simulator.scale_x
        s_y = self.simulator.scale_y
        if self.display["body"] == 1:
            x1, y1, x2, y2 = s_x(self._gx - self.radius), s_y(self._gy - self.radius), s_x(self._gx + self.radius), s_y(self._gy + self.radius)
            self.simulator.canvas.create_oval(x1, y1, x2, y2, fill=self.color, tag="robot-%s" % self.name, outline="black")
        if self.display["boundingBox"] == 1 and self.boundingBox != []:
            # Body Polygon, by x and y lists:
            a90 = self._ga + 90 * PIOVER180 # angle is 90 degrees off for graphics
            xy = map(lambda x, y: (s_x(self._gx + x * math.cos(a90) - y * math.sin(a90)),
                                   s_y(self._gy + x * math.sin(a90) + y * math.cos(a90))),
                     self.boundingBox[0], self.boundingBox[1])
            self.simulator.canvas.create_polygon(xy, tag="robot-%s" % self.name, fill="", outline="purple")
        self.addMouseBindings()

class TkPioneer(TkRobot):
    def __init__(self, *args, **kwargs):
        TkRobot.__init__(self, *args, **kwargs)
        self.radius = 0.4

    def draw(self):
        """
        Draws the body of the robot. Not very efficient.
        """
        if  self._last_pose == (self._gx, self._gy, self._ga): return # hasn't moved
        self._last_pose = (self._gx, self._gy, self._ga)
        self.simulator.canvas.delete("robot-%s" % self.name)
        # Body Polygon, by x and y lists:
        sx = [.225, .15, -.15, -.225, -.225, -.15, .15, .225]
        sy = [.08, .175, .175, .08, -.08, -.175, -.175, -.08]
        s_x = self.simulator.scale_x
        s_y = self.simulator.scale_y
        a90 = self._ga + 90 * PIOVER180 # angle is 90 degrees off for graphics
        if self.display["body"] == 1:
            xy = map(lambda x, y: (s_x(self._gx + x * math.cos(a90) - y * math.sin(a90)),
                                   s_y(self._gy + x * math.sin(a90) + y * math.cos(a90))),
                     sx, sy)
            self.simulator.canvas.create_polygon(xy, fill=self.color, tag="robot-%s" % self.name, outline="black")
            bx = [ .14, .06, .06, .14] # front camera
            by = [-.06, -.06, .06, .06]
            xy = map(lambda x, y: (s_x(self._gx + x * math.cos(a90) - y * math.sin(a90)),
                                   s_y(self._gy + x * math.sin(a90) + y * math.cos(a90))),
                     bx, by)
            self.simulator.canvas.create_polygon(xy, tag="robot-%s" % self.name, fill="black")
            if self.bulb:
                radius = .05 * self.simulator.scale
                x = s_x(self._gx + self.bulb.x * math.cos(a90) - self.bulb.y * math.sin(a90))
                y = s_y(self._gy + self.bulb.x * math.sin(a90) + self.bulb.y * math.cos(a90))
                # color based on robot, or value?
                color = "#%02x%02x%02x" % (min(max(self.bulb.brightness * 255,0),255),
                                           min(max(self.bulb.brightness * 255,0),255), 0) # amount of yellow
                # need to scale this bulb:
                self.simulator.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                                  tag="robot-%s" % self.name, fill=color, outline="black")
            if self.gripper:
                # build a polygon around gripper line:
                xs = []
                ys = []
                for i in range(0, len(self.gripper.boundingSeg[0]), 2):
                    xs.append(self.gripper.boundingSeg[0][i]);     ys.append(self.gripper.boundingSeg[1][i] + .01)
                    xs.append(self.gripper.boundingSeg[0][i + 1]); ys.append(self.gripper.boundingSeg[1][i + 1] + .01)
                    xs.append(self.gripper.boundingSeg[0][i + 1]); ys.append(self.gripper.boundingSeg[1][i + 1] - .01)
                    xs.append(self.gripper.boundingSeg[0][i]);     ys.append(self.gripper.boundingSeg[1][i] - .01)
                xy = map(lambda x, y: (s_x(self._gx + x * math.cos(a90) - y * math.sin(a90)),
                                       s_y(self._gy + x * math.sin(a90) + y * math.cos(a90))),
                         xs, ys)
                self.simulator.canvas.create_polygon(xy, tag="robot-%s" % self.name, fill="black", outline="black")
        if self.display["boundingBox"] == 1:
            if self.boundingBox != []:
                xy = map(lambda x, y: (s_x(self._gx + x * math.cos(a90) - y * math.sin(a90)),
                                       s_y(self._gy + x * math.sin(a90) + y * math.cos(a90))),
                         self.boundingBox[0], self.boundingBox[1])
                self.simulator.canvas.create_polygon(xy, tag="robot-%s" % self.name, fill="", outline="purple")
            if self.boundingSeg != []:
                xy = map(lambda x, y: (s_x(self._gx + x * math.cos(a90) - y * math.sin(a90)),
                                       s_y(self._gy + x * math.sin(a90) + y * math.cos(a90))),
                         self.boundingSeg[0], self.boundingSeg[1])
                for i in range(0, len(xy), 2):
                    self.simulator.canvas.create_line(xy[i][0], xy[i][1],
                                                      xy[i + 1][0], xy[i + 1][1],
                                                      tag="robot-%s" % self.name, fill="purple")
        self.addMouseBindings()

class RangeSensor:
    def __init__(self, name, geometry, arc, maxRange, noise = 0.0):
        self.type = name
        # geometry = (x, y, a) origin in meters and radians
        self.geometry = geometry
        self.arc = arc
        self.maxRange = maxRange
        self.noise = noise
        self.groups = {}
        self.scan = [0] * len(geometry) # for data
class Light:
    def __init__(self, x, y, brightness, color="yellow"):
        self.x = x
        self.y = y
        self.brightness = brightness
        self.color = color
        self._xyb = x, y, brightness # original settings for reset
        self.rgb = colorMap[color]
        self.type = "fixed"
class BulbDevice(Light):
    """
    Bulb will have color of robot.
    """
    def __init__(self, x, y):
        Light.__init__(self, x, y, 1.0)
        self.type = "bulb"
        self.geometry = (0, 0, 0)
class LightSensor:
    def __init__(self, geometry, noise = 0.0):
        self.type = "light"
        self.geometry = geometry
        self.arc = None
        self.maxRange = 1000.0
        self.noise = noise
        self.groups = {}
        self.scan = [0] * len(geometry) # for data
        self.rgb = [[0,0,0] for g in geometry]

class Gripper:
    def __init__(self, boundingSeg, breakBeam = []):
        self.type = "gripper"
        self.scan = []
        self.objs = []
        self.state = "open"
        self.boundingSeg = boundingSeg
        self.breakBeam = breakBeam
    def close(self):
        for segment in self.objs:
            segment.robot.setPose(-1000.0, -1000.0, 0.0)
        self.objs = []
        return "ok"

class Camera:
    def __init__(self, width, height, startAngle, stopAngle, x, y, thr):
        self.type = "camera"
        self.scan = []
        self.width = width
        self.height = height
        self.startAngle = startAngle
        self.stopAngle = stopAngle
        self.pose = (x, y, thr)
        self.color = [[0,0,0] for i in range(self.width)]
        self.range = [0 for i in range(self.width)]

class PioneerFrontSonars(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
            "sonar", geometry = (( 0.10, 0.175, 90 * PIOVER180),
                                 ( 0.17, 0.15, 65 * PIOVER180),
                                 ( 0.20, 0.11, 40 * PIOVER180),
                                 ( 0.225, 0.05, 15 * PIOVER180),
                                 ( 0.225,-0.05,-15 * PIOVER180),
                                 ( 0.20,-0.11,-40 * PIOVER180),
                                 ( 0.17,-0.15,-65 * PIOVER180),
                                 ( 0.10,-0.175,-90 * PIOVER180)),
            arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
        self.groups = {'all': range(8),
                       'front': (3, 4),
                       'front-left' : (1,2,3),
                       'front-right' : (4, 5, 6),
                       'front-all' : (1,2, 3, 4, 5, 6),
                       'left' : (0,), 
                       'right' : (7,), 
                       'left-front' : (1,2), 
                       'right-front' : (5,6, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}
        
class Pioneer16Sonars(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
            "sonar", geometry = (( 0.10, 0.175, 90 * PIOVER180),
                                 ( 0.17, 0.15, 65 * PIOVER180),
                                 ( 0.20, 0.11, 40 * PIOVER180),
                                 ( 0.225, 0.05, 15 * PIOVER180),
                                 ( 0.225,-0.05,-15 * PIOVER180),
                                 ( 0.20,-0.11,-40 * PIOVER180),
                                 ( 0.17,-0.15,-65 * PIOVER180),
                                 ( 0.10,-0.175,-90 * PIOVER180),
                                 ( -0.10,-0.175,-90 * PIOVER180),
                                 ( -0.17,-0.15, (180 + 65) * PIOVER180),
                                 ( -0.20,-0.11, (180 + 40) * PIOVER180),
                                 ( -0.225,-0.05,(180 + 15) * PIOVER180),
                                 ( -0.225, 0.05,(180 - 15) * PIOVER180),
                                 ( -0.20, 0.11, (180 - 40) * PIOVER180),
                                 ( -0.17, 0.15, (180 - 65) * PIOVER180),
                                 ( -0.10, 0.175,(180 - 90) * PIOVER180)),
            arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
        self.groups = {'all': range(16),
                       'front': (3, 4),
                       'front-left' : (1,2,3),
                       'front-right' : (4, 5, 6),
                       'front-all' : (1,2, 3, 4, 5, 6),
                       'left' : (0, 15), 
                       'right' : (7, 8), 
                       'left-front' : (0,), 
                       'right-front' : (7, ),
                       'left-back' : (15, ),
                       'right-back' : (8, ),
                       'back-right' : (9, 10, 11),
                       'back-left' : (12, 13, 14), 
                       'back' : (11, 12),
                       'back-all' : ( 9, 10, 11, 12, 13, 14)}
        
class PioneerFrontLightSensors(LightSensor):
    def __init__(self):
        # make sure outside of bb!
        LightSensor.__init__(self, ((.225,  .175, 0), (.225, -.175, 0)),
                             noise=0.0) 
        self.groups = {"front-all": (0, 1),
                       "all": (0, 1),
                       "front": (0, 1),
                       "front-left": (0, ),
                       "front-right": (1, ),
                       'left' : (0,), 
                       'right' : (1,), 
                       'left-front' : (0,), 
                       'right-front' : (1, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}
    
