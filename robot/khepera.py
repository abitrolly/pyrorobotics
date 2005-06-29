# Defines KheperaRobot, a subclass of robot

from pyrobot.system.share import config
from pyrobot.robot import *
from pyrobot.robot.device import *
from pyrobot.system.serial import *
import pyrobot.gui.console as console
import string, array, math 
from time import sleep
from pyrobot.simulators.khepera.CNTRL import _ksim as ksim
from pyrobot.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

class IRSensor(Device):
    def __init__(self, dev, type = "ir"):
        Device.__init__(self, type)
        self.dev = dev
        self.devData['units']    = "ROBOTS" # current report units
        self.devData["radius"] = 55 / 1000.0 # meters
        # natural units:
        self.devData["rawunits"] = "CM"
        self.devData['maxvalueraw'] = 6.0 # in rawunits
        # ----------------------------------------------
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])
        self.devData["count"] = 8
        self.groups = {'all': range(8),
                       'front' : (2, 3), 
                       'front-left' : (0, 1), 
                       'front-right' : (4, 5),
                       'front-all' : (1, 2, 3, 4),
                       'left' : (0, ), 
                       'right' : (5, ), 
                       'left-front' : (0, ), 
                       'right-front' : (5, ), 
                       'left-back' : (7, ), 
                       'right-back' : (6, ), 
                       'back-left' : (7, ), 
                       'back-right' : (6, ), 
                       'back-all' : (6, 7), 
                       'back' : (6, 7)} 
        self.subDataFunc['ox']    = self.ox
        self.subDataFunc['oy']    = self.oy
        self.subDataFunc['oz']    = lambda pos: 0.0
        self.subDataFunc['th']    = self.th
        self.subDataFunc['thr']    = lambda pos: self.th(pos) * PIOVER180
        self.subDataFunc['arc']   = lambda pos: (15 * PIOVER180)
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = self.getGroupNames
        self.subDataFunc['x'] = self.hitX
        self.subDataFunc['y'] = self.hitY
	self.subDataFunc['z'] = self.hitZ
	self.subDataFunc['value'] = self.getIRRange
        self.startDevice()    

    def __len__(self):
        return self.devData["count"]
    def getSensorValue(self, pos):
        return SensorValue(self, self.getVal(pos), pos,
                           (self.ox(pos), self.oy(pos), 0.0, self.th(pos)))
    
    def postSet(self, keyword):
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])

    def ox(self, pos):
        # in mm
        if pos == 0:
            retval = 10.0
        elif pos == 1:
            retval = 20.0
        elif pos == 2:
            retval = 30.0
        elif pos == 3:
            retval = 30.0 
        elif pos == 4:
            retval = 20.0
        elif pos == 5:
            retval = 10.0
        elif pos == 6:
            retval = -30.0
        elif pos == 7:
            retval = -30.0
        return retval

    def oy(self, pos):
        # in mm
        if pos == 0:
            retval = 30.0
        elif pos == 1:
            retval = 20.0
        elif pos == 2:
            retval = 10.0
        elif pos == 3:
            retval = -10.0 
        elif pos == 4:
            retval = -20.0
        elif pos == 5:
            retval = -30.0
        elif pos == 6:
            retval = -10.0
        elif pos == 7:
            retval = 10.0
        return retval

    def th(self, pos):
        if pos == 0:
            return 90.0
        elif pos == 1:
            return 45.0
        elif pos == 2:
            return 0.0
        elif pos == 3:
            return 0.0 
        elif pos == 4:
            return -45.0
        elif pos == 5:
            return -90.0
        elif pos == 6:
            return 180.0
        elif pos == 7:
            return 180.0

    def getVal(self, pos):
        try:
            return (1023 - self.dev.senseData['ir'][pos])/1023.0 * 6.0
        except:
            return 0

    def getIRRange(self, pos):
        data = self.getVal(pos)
        return self.rawToUnits(data)

    def hitX(self, pos):
        # convert to x,y relative to robot
        dist = self.getVal(pos)
        angle = (-self.th(pos)  - 90.0) / 180.0 * math.pi
        return dist * math.cos(angle)
        
    def hitY(self, pos):
        # convert to x,y relative to robot
        dist = self.getVal(pos)
        angle = (-self.th(pos) - 90.0) / 180.0 * math.pi
        return dist * math.sin(angle)

    def hitZ(self, pos): return 0.0

class LightSensor(IRSensor):
    def __init__(self, dev):
        IRSensor.__init__(self, dev, "light")
        # now, just overwrite those differences
        self.devData['units'] = "RAW"
        self.devData["maxvalueraw"] = 511.0
        self.devData['maxvalue'] = self.devData["maxvalueraw"]
	self.subDataFunc['value'] = self.getLightRange

    def __len__(self):
        return self.devData["count"]
    def getSensorValue(self, pos):
        return SensorValue(self, self.dev.senseData['light'][pos], pos,
                           (self.ox(pos), self.oy(pos), 0.0, self.th(pos)))
    
    def postSet(self, kw):
        self.devData['maxvalue'] = self.devData["maxvalueraw"]

    def getLightRange(self, pos):
        try:
            data = self.dev.senseData['light'][pos]
        except:
            print "not enough sensor data"
            return 0.0
        return data

class SerialSimulator:
    def __init__(self):
        self.p = ksim.initControl()
        self.last_msg = []
        
    def writeline(self, msg, newline = "\n"):
        self.last_msg.append(ksim.sendMessage(self.p, msg))
        sleep(.01)  # for some reason it seems as if python doesn't block
		    # properly on the preceeding assignment unless this is here

    def readline(self): # 1 = block till we get something
        if len(self.last_msg): return self.last_msg.pop(0)
        return ''

    def readlines(self):
        retval = []
        while len(self.last_msg) > 0: retval.append(self.last_msg.pop(0))
        return retval

    def inWaiting(self):
        return len(self.last_msg)
    
class KheperaRobot(Robot):
    def __init__(self,
                 port = None,
                 simulator = 0,
                 rate = None,
                 subtype = "Khepera"):
        # simulator = 0 makes it real
        Robot.__init__(self) # robot constructor
        self.buffer = ''
        self.debug = 0
        self.pause = 0.1
        if simulator == 1:
            self.sc = SerialSimulator()
            port = "simulated"
            print "K-Team opening simulation..."
        else:
            if subtype == "Khepera":
                if port == None:
                    try:
                        port = config.get('khepera', 'port')
                    except:
                        pass
                if port == None:
                    port = "/dev/ttyS0"
                if rate == None:
                    rate = 38400
            else:
                if port == None:
                    try:
                        port = config.get('hemisson', 'port')
                    except:
                        pass
                if port == None:
                    port = "/dev/ttyUB0"
                if rate == None:
                    rate = 115200
            print "K-Team opening port", port, "..."
            self.sc = Serial(port, baudrate=rate) #, xonxoff=0, rtscts=0)
            self.sc.setTimeout(0)
            self.sc.readlines() # to clear out the line
        self.stallTolerance = 0.25
        self.stallHistoryPos = 0
        self.stallHistorySize = 5
        self.stallHistory = [0] * self.stallHistorySize
        self.lastTranslate = 0
        self.lastRotate = 0
        self.currSpeed = [0, 0]
        # This could go as high as 127, but I am keeping it small
        # to be on the same scale as larger robots. -DSB
        self.translateFactor = 30
        self.rotateFactor = 12
        self.dataTypes = {'n': 'ir',
                          'h' : 'position',
                          'o' : 'light',
                          'k' : 'stall',
                          'e' : 'speed',
                          'b' : 'version',
                          'j' : 'extensionDevices',
                          't1b'  : 'gripper software',
                          't1f'  : 'gripper resistivity',
                          't1g'  : 'gripper beam state',
                          't1h1' : 'gripper arm position',
                          't1h0' : 'gripper state',
                          't1j'  : 'gripper jumpers'
                          }
        self.senseData = {}
        self.senseData['position'] = [0] * 3
        self.senseData['ir'] = [0] * 6
        self.senseData['light'] = [0] * 6
        self.senseData['stall'] = [0] * 6
        self.devData["subtype"] = subtype
        if subtype == "Hemisson":
            self.devData["builtinDevices"] = ['ir', 'light', 'audio']
            self.newline = "\r"
        elif subtype == "Khepera":
            self.devData["builtinDevices"] = ['ir', 'light', 'gripper']
            self.newline = "\n"
        else:
            raise TypeError, "invalid K-Team subtype: '%s'" % subtype
        self.startDevice("ir")
        self.devDataFunc["range"] = self.get("/devices/ir0/object")
        self.devDataFunc["ir"] = self.get("/devices/ir0/object")
        self.startDevice("light")
        self.devDataFunc["light"] = self.get("/devices/light0/object")
        if subtype == "Khepera":
            self.sendMsg('H') # position
        else:
            self.senseData["position"] = 0, 0
            self.sendMsg('B') # version
            self.sendMsg('j') # extensionDevices
        self.x = 0.0
        self.y = 0.0
        self.thr = 0.0
        self.th = 0.0
        try:
            self.w0 = self.senseData['position'][0]
            self.w1 = self.senseData['position'][1]
        except:
            raise "KTeamConnectionError"
        self.devData["type"] = "K-Team"
        self.devData["port"] = port
        self.devData["simulated"] = simulator
        if subtype == "Khepera":
            self.devData['radius'] = 55.0 # in MM
        else:
            self.devData['radius'] = 120.0 # in MM
        # ----- Updatable things:
        self.devData['stall'] = self.isStall()
        self.devData['x'] = self.getX()
        self.devData['y'] = self.getY()
        self.devData['z'] = self.getZ()
        self.devData['th'] = self.getTh() # in degrees
        self.devData['thr'] = self.getThr() # in radians
        self.devData["supportedFeatures"].append( "odometry" )
        self.devData["supportedFeatures"].append( "continuous-movement" )
        self.devData["supportedFeatures"].append( "range-sensor" )
	self.update() 
        self.inform("Done loading K-Team robot.")

    def startDeviceBuiltin(self, item):
        if item == "ir":
            return {"ir": IRSensor(self)}
        elif item == "light":
            return {"light": LightSensor(self)}
        elif item == "gripper":
            return {"gripper": Gripper(self)}
        else:
            raise AttributeError, "K-Team robot does not support device '%s'" % item

    def disconnect(self):
        self.stop()

    def sendMsg(self, msg):
        if self.debug: print "DEBUG: sendMsg:", msg
        self.sc.writeline(msg, self.newline)
        if self.devData["subtype"] == "Hemisson":
            sleep(self.pause)

    def readData(self):
        if self.sc.inWaiting() == 0: return
        retval = self.sc.readline() # 1 = block till we get something
        #print "DEBUG:", retval
        if len(retval) > 0:
            if retval[-1] != '\n' and retval[-1] != '\r':
                self.buffer += retval
            else:
                self.buffer += retval.strip()
                if len(self.buffer) > 0:
                    rawdata = string.split(self.buffer, ",")
                    self.buffer = ''
                    if self.debug: print "DEBUG: read:", rawdata
                    dtype, data = rawdata[0], rawdata[1:]
                    if dtype == 't':
                        if len(data) < 2:
                            self.buffer = ''
                            if self.debug: print "K-Team turret packet error:", rawdata
                            return
                        else:
                            dtype += data[0] + data[1]
                            data = data[2:]
                    key = self.dataTypes.get(dtype, None)
                    if key != None:
                        try:
                            self.senseData[key] = map(int,data)
                        except:
                            #pass
                            if self.debug: print "K-Team packet error:", rawdata

    def update(self):
        self._update()
        if self.devData["subtype"] == "Khepera":
            self.sendMsg('N') #, 'ir')     # proximity
            self.sendMsg('O') #, 'light')  # ambient light
            self.sendMsg('H') #, 'position')
            self.sendMsg('E') #, 'speed')
            self.sendMsg('K') #, 'stall')  # motor status, used by isStall
            gripperID = self.hasA('gripper')
            if gripperID:
                #self.sendMsg('T,1,H,0')  # gripper state
                #self.sendMsg('T,1,H,1')  # arm position
                self.sendMsg('T,1,G')    # gripper beam state
                self.sendMsg('T,1,F')    # gripper resistivity
                
        elif self.devData["subtype"] == "Hemisson":
            self.sendMsg('N') #, 'ir')     # proximity
            self.sendMsg('O') #, 'light')  # ambient light
        while self.sc.inWaiting(): self.readData()
        """
        The 'K' message returns 6 numbers dealing with the status of the
        motors.  The 3rd and 6th are error codes representing the left and
        right motors, respectively.  The represent the difference
        between the desired speed and the actual speed.
        """
        # ----------- start compute stall
        self.stallHistory[self.stallHistoryPos] = 0
        try:
            if self.currSpeed[0] != 0:
                err = abs(float(self.senseData['stall'][2])/float(self.currSpeed[0]) - 1)
                if err < .25:
                    self.stallHistory[self.stallHistoryPos] = 1
            if self.currSpeed[1] != 0:
                err = abs(float(self.senseData['stall'][5])/float(self.currSpeed[1]) - 1)
                if err < .25:
                    self.stallHistory[self.stallHistoryPos] = 1
        except:
            pass
        # ----------- end compute stall
        self.stallHistoryPos = (self.stallHistoryPos + 1) % self.stallHistorySize
        self.devData['stall'] = self.isStall()
        self.devData['x'] = self.getX()
        self.devData['y'] = self.getY()
        self.devData['z'] = self.getZ()
        self.devData['th'] = self.getTh() # in degrees
        self.devData['thr'] = self.getThr() # in radians

        self.deadReckon()

    def deadReckon(self):
        """
        Called after each little update in position.
        Based on code from Adam R. Bockrath
        http://www.dcs.qmul.ac.uk/~adamb/
        """
        # get wheel positions:
        try:
            w0 = self.senseData['position'][0]
            w1 = self.senseData['position'][1]
        except:
            return
        if w0 == self.w0 and w1 == self.w1:
            # no difference to compute
            return
        # get diff:
        delta_w0 = (w0 - self.w0) # in ticks
        delta_w1 = (w1 - self.w1) # in ticks
        # get diff / diameter of wheel base, in ticks:
        delta_thr   = (delta_w1 - delta_w0) / 644.5
        # average diff (dist):
        delta_dist = (delta_w0 + delta_w1) / 2.0
        # compute change in x, y:
        delta_x = delta_dist * math.cos(self.thr + delta_thr/2.0)
        delta_y = delta_dist * math.sin(self.thr + delta_thr/2.0)
        if delta_thr != 0:
            delta_x *= 2.0 * math.sin(delta_thr/2.0) / delta_thr
            delta_y *= 2.0 * math.sin(delta_thr/2.0) / delta_thr
        # update everything:
        # FIX: I think that this needs to be subtracted for our th?
        self.thr += delta_thr
        # keep thr in range 0 - 2pi:
        while (self.thr > 2.0 * math.pi):
            self.thr -= (2.0 * math.pi)
        while (self.thr < 0):
            self.thr += (2.0 * math.pi)
        # save old values:
        self.w0 = w0
        self.w1 = w1
        self.x += (delta_x * .08) # convert ticks to mm
        self.y += (delta_y * .08) # convert ticks to mm
        self.th = self.thr * (180.0 / math.pi)

    def isStall(self, dev = 0):
        stalls = float(reduce(lambda x, y: x + y, self.stallHistory))
        # if greater than % of last history is stall, then stall
        return (stalls / self.stallHistorySize) > 0.5

    def getX(self, dev = 0):
        #return self.mmToUnits(self.x, self.devData['units'](dev))
        return self.x / 1000.0
    
    def getY(self, dev = 0):
        #return self.mmToUnits(self.y, self.devData['units'](dev))
        return self.y / 1000.0
    
    def getZ(self, dev = 0):
        return 0
    
    def getTh(self, dev = 0):
        return self.th

    def getThr(self, dev = 0):
        return self.thr

    def move(self, trans, rotate):
        self.lastTranslate = trans
        self.lastRotate = rotate
        # FIX: do min/max here
        self.adjustSpeed()

    def adjustSpeed(dev):
        # This will send new motor commands based on the
        # robot's lastTranslate and lastRotate settings.
        # Khepera has differential drive, so compute each
        # side motor commands:
        left  = int((dev.lastTranslate * dev.translateFactor - \
                     dev.lastRotate * dev.rotateFactor))
        right  = int((dev.lastTranslate * dev.translateFactor + \
                      dev.lastRotate * dev.rotateFactor))
        # FIX: add acceleration, and assume that adjustSpeed
        # is being continuously called.
        dev.currSpeed = [left, right]
        dev.sendMsg('D,%i,%i' % (left, right))
        
    def translate(dev, value):
        dev.lastTranslate = value
        dev.adjustSpeed()
    
    def rotate(dev, value):
        dev.lastRotate = value
        dev.adjustSpeed()
    
    def localize(self, x = 0.0, y = 0.0, th = 0.0):
        self.x = x * 1000
        self.y = y * 1000
        self.th = th
        self.thr = self.th * PIOVER180
    
class Gripper(Device):
    def __init__(self, robot, type = "gripper"):
        Device.__init__(self, type)
        self.robot = robot
        self.robot.sendMsg('T,1,B')    # gripper software version
        self.robot.sendMsg('T,1,J')    # gripper jumpers
        self.lowestArmPosition = 255
        self.highestArmPosition = 165
        self.liftUpPosition = 175
        self.putDownPosition = 240
        self.startDevice()

    # preGet methods
    def getGripState(self):
        gripState = self.robot.senseData['FIX ME'][0]
        if gripState < 100:
            return 'closed'
        else:
            return 'open'

    def getBreakBeamState(self):
        beamState = self.robot.senseData['gripper beam state'][0]
        if beamState < 100:
            return 'nothing'
        else:
            return 'something'

    def getArmPosition(self):
        return self.robot.senseData['gripper arm position'][0]

    def getResistivity(self):
        return self.robot.senseData['gripper resistivity'][0]

    def getSoftwareVersion(self):
        version, revision = self.robot.senseData['gripper software'][0:2]
        return version + 0.1 * revision

    def isClosed(self):
        return self.getGripState() == 'closed'

    def isGripMoving(self):
        pass

    def isLiftMoving(self):
        pass

    def isLiftMaxed(self):
        return self.getArmPosition() == self.highestArmPosition

    # postSet methods
    def gripOpen(self):
        self.robot.sendMsg('T,1,D,0')

    def gripClose(self):
        self.robot.sendMsg('T,1,D,1')

    def gripStop(self):
        pass

    def setArmPosition(self, angle):
        if angle > self.lowestArmPosition:
            angle = self.lowestArmPosition
        elif angle < self.highestArmPosition:
            angle = self.highestArmPosition
        self.robot.sendMsg('T,1,E,' + str(angle))

    def liftUp(self):
        self.setArmPosition(self.liftUpPosition)

    def liftDown(self):
        self.setArmPosition(self.putDownPosition)

    def gripperStore(self):
        self.gripClose()
        self.liftUp()

    def gripperDeploy(self):
        self.liftDown()
        self.gripOpen()

    def gripperHalt(self):
        pass

if __name__ == '__main__':
    x = KheperaRobot()
    x.update()
    x.GetMin()
