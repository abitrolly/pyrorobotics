# Defines KheperaRobot, a subclass of robot

from pyro.system.share import config
from pyro.robot import *
from pyro.robot.device import *
from pyro.system.SerialConnection import *
import pyro.robot.driver as driver
import pyro.gui.console as console
import string, array, math, termios
from time import sleep
from pyro.simulators.khepera.CNTRL import _ksim as ksim

PIOVER180 = math.pi / 180.0
DEG90RADS = 0.5 * math.pi
COSDEG90RADS = math.cos(DEG90RADS) / 1000.0
SINDEG90RADS = math.sin(DEG90RADS) / 1000.0

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
        self.subDataFunc['oz']    = lambda pos: 0.03
        self.subDataFunc['th']    = self.th
        self.subDataFunc['thr']    = lambda pos: self.th(pos) / PIOVER180
        self.subDataFunc['arc']   = lambda pos: (15 * PIOVER180)
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = lambda pos: self.getGroupNames(pos)
	self.subDataFunc['x'] = self.getIRXCoord
	self.subDataFunc['y'] = self.getIRYCoord
	self.subDataFunc['z'] = lambda pos: 0.03
	self.subDataFunc['value'] = self.getIRRange
        #self.subDataFunc['all'] = self.getIRRangeAll
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])
	self.subDataFunc['flag'] = self.getIRFlag
        self.startDevice()    

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

    def getIRRange(self, pos):
        try:
            data = self.devData["maxvalueraw"] - \
                   (self.dev.senseData['ir'][pos] / 1023.0 * 6.0)
        except:
            print "not enough sensor data"
            return 0.0
        data = max(min(data, self.devData["maxvalueraw"]), 0)
        return self.rawToUnits(data)

    def getIRXCoord(self, dev, pos):
        # convert to x,y relative to robot
        data = self.getIRRange(pos)
        dist = self.rawToUnits(data)
        angle = (-self.light_thd(dev, pos)  - 90.0) / 180.0 * math.pi
        return dist * math.cos(angle)
        
    def getIRYCoord(self, dev, pos):
        # convert to x,y relative to robot
        data = self.getIRRange(pos)
        dist = self.rawToUnits(data)
        angle = (-self.light_thd(pos) - 90.0) / 180.0 * math.pi
        return dist * math.sin(angle)
    
    def getIRFlag(self, pos):
        return 0

class LightSensor(IRSensor):
    def __init__(self, dev):
        IRSensor.__init__(self, dev, "light")
        # now, just overwrite those differences
        self.devData['units'] = "RAW"
        self.devData["maxvalueraw"] = 511.0
        self.devData['maxvalue'] = self.devData["maxvalueraw"]
	self.subDataFunc['value'] = self.getLightRange
	self.subDataFunc['flag'] = self.getIRFlag

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
        self.last_msg = ''
        
    def writeline(self, msg):
        self.last_msg = ksim.sendMessage(self.p, msg)
        sleep(.01)  # for some reason it seems as if python doesn't block
		    # properly on the preceeding assignment unless this is here

    def readline(self): # 1 = block till we get something
        return self.last_msg #+ ',0,0,0,0,0,0,0,0'
    
class KheperaRobot(Robot):
    def __init__(self, port = None, simulator = 0): # 0 makes it real
        Robot.__init__(self) # robot constructor
        if simulator == 1:
            self.sc = SerialSimulator()
            port = "simulated"
            print "Khepera opening simulation..."
        else:
            try:
                port = config.get('khepera', 'port')
            except:
                pass
            if port == None:
                port = "/dev/ttyS1"
            print "Khepera opening port", port, "..."
            self.sc = SerialConnection(port, termios.B38400)
            #self.sc = SerialConnection("/dev/ttyS1", termios.B115200)
            #self.sc = SerialConnection("/dev/ttyS1", termios.B57600)
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
        self.senseData = {}
        self.senseData['position'] = []
        self.senseData['ir'] = []
        self.senseData['light'] = []
        self.senseData['stall'] = []
        
        self.devData["builtinDevices"] = ['ir', 'light']
        self.startDevice("ir")
        self.devDataFunc["range"] = self.get("/devices/ir0/object")
        self.devDataFunc["ir"] = self.get("/devices/ir0/object")
        self.startDevice("light")
        self.devDataFunc["light"] = self.get("/devices/light0/object")

        self.sendMsg('H', 'position')
        self.x = 0.0
        self.y = 0.0
        self.thr = 0.0
        self.th = 0.0
        try:
            self.w0 = self.senseData['position'][0]
            self.w1 = self.senseData['position'][1]
        except:
            raise "KheperaConnectionError"
        self.devData["type"] = "Khepera"
        self.devData["subtype"] = "khepera1"
        self.devData["port"] = port
        self.devData["simulated"] = simulator
        self.devData['radius'] = 55.0 # in MM
        # ----- Updatable things:
        self.devData['stall'] = self.isStall()
        self.devData['x'] = self.getX()
        self.devData['y'] = self.getY()
        self.devData['z'] = self.getZ()
        self.devData['th'] = self.getTh() # in degrees
        self.devData['thr'] = self.getThr() # in radians

	self.update() 
        self.inform("Done loading khepera robot.")

    def startDeviceBuiltin(self, item):
        if item == "ir":
            return {"ir": IRSensor(self)}
        elif item == "light":
            return {"light": LightSensor(self)}
        else:
            raise AttributeError, "khepera robot does not support device '%s'" % item

    def disconnect(self):
        self.stop()

    def sendMsg(self, msg, data = '', type = 'i'):
        # Fix: this needs to be two processes: one write Queue
        # and one read Queue.
        #print "SENDING:", msg
        tries = 0
        done = 0
        while tries < 5 and not done:
            try:
                self.sc.writeline(msg)
                retval = self.sc.readline() # 1 = block till we get something
                #print retval
                if retval[0].upper() == msg[0]:
                    done = 1
                else:
                    tries += 1
            except:
                tries += 1
        if done == 0:
            #print "khepera serial read/write error..."
            self.senseData[data] = array.array(type, [0] * 20)
            return
        if data:
            lines = string.split(retval, "\r\n")
            for line in lines:
                if not line == '':
                    # print "processing line:", line
                    irs = string.split(line, ",")
                    irs = irs[1:]
                    #print "RECEIVE data:", data, retval
                    try:
                        self.senseData[data] = array.array(type, map(int, irs))
                    except:
                        self.senseData[data] = array.array(type, [0] * 20)
                        print "khepera packet error: type=", data, "vals=", irs
            return self.senseData[data]
        
    def update(self):
        self._update()
        self.sendMsg('N', 'ir')     # proximity
        self.sendMsg('O', 'light')  # ambient light
        self.sendMsg('H', 'position')
        self.sendMsg('E', 'speed')
        self.sendMsg('K', 'stall')  # motor status, used by isStall
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
    
if __name__ == '__main__':
    x = KheperaRobot()
    x.update()
    x.GetMin()
