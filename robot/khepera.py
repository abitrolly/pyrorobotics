# Defines KheperaRobot, a subclass of robot

from pyro.system.share import config
from pyro.robot import *
from pyro.system.SerialConnection import *
import pyro.robot.driver as driver
import pyro.gui.console as console
import string
import array
import math
import termios
from time import sleep

from pyro.simulators.khepera.CNTRL import _ksim as ksim

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
    def __init__(self, name = None, simulator = 0): # 0 makes it real
        Robot.__init__(self, name, "khepera") # robot constructor
        self.simulated = simulator
        if simulator == 1:
            self.sc = SerialSimulator()
        else:
            try:
                port = config.get('khepera', 'port')
            except:
                port = "/dev/ttyS1"
            if not port:
                port = "/dev/ttyS1"
            print "Khepera opening port", port, "..."
            self.sc = SerialConnection(port, termios.B38400)
            #self.sc = SerialConnection("/dev/ttyS1", termios.B115200)
            #self.sc = SerialConnection("/dev/ttyS1", termios.B57600)
        self.dev = self # pointer to self
        self.stallTolerance = 0.25
        self.stallHistoryPos = 0
        self.stallHistorySize = 5
        self.stallHistory = [0] * self.stallHistorySize
        self.sensorSet = {'all': range(8),
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
        self.senseData = {}
        self.lastTranslate = 0
        self.lastRotate = 0
        self.currSpeed = [0, 0]
        # This could go as high as 127, but I am keeping it small
        # to be on the same scale as larger robots. -DSB
        self.translateFactor = 30
        self.rotateFactor = 12
        self.inform("Loading Khepera robot interface...")

	# robot senses (all are functions):
        self.senses['robot'] = {}
        self.senses['robot']['simulator'] = lambda self, x = simulator: x
        self.senses['robot']['stall'] = self.isStall
        self.senses['robot']['x'] = self.getX
        self.senses['robot']['y'] = self.getY
        self.senses['robot']['z'] = self.getZ
        self.senses['robot']['radius'] = lambda self: 55.0 # in MM
        self.senses['robot']['th'] = self.getTh # in degrees
        self.senses['robot']['thr'] = self.getThr # in radians
	self.senses['robot']['type'] = lambda self: 'khepera'
        self.senses['robot']['units'] = lambda self: 'CM'

	self.senses['robot']['name'] = lambda self: 'khepera-1'

	self.senses['ir'] = {}
	self.senses['ir']['count'] = lambda self: 8
	self.senses['ir']['type'] = lambda self: 'range'

	# location of sensors' hits:
	self.senses['ir']['x'] = self.getIRXCoord
	self.senses['ir']['y'] = self.getIRYCoord
	self.senses['ir']['z'] = lambda self, pos: 0.03
	self.senses['ir']['value'] = self.getIRRange
        self.senses['ir']['all'] = self.getIRRangeAll
        self.senses['ir']['maxvalue'] = self.getIRMaxRange
	self.senses['ir']['flag'] = self.getIRFlag
        self.senses['ir']['units'] = lambda self: "ROBOTS"

	# location of origin of sensors:
        self.senses['ir']['ox'] = self.light_ox
	self.senses['ir']['oy'] = self.light_oy
	self.senses['ir']['oz'] = lambda self, pos: 0.03 # meters
	self.senses['ir']['th'] = self.light_th
        # in radians:
        self.senses['ir']['arc'] = lambda self, pos, \
                                      x = (15 * math.pi / 180) : x
        # Make a copy, for default:
        self.senses['range'] = self.senses['ir']

	self.senses['light'] = {}
	self.senses['light']['count'] = lambda self: 8
	self.senses['light']['type'] = lambda self: 'measure'
        self.senses['light']['maxvalue'] = self.getLightMaxRange
        self.senses['light']['units'] = lambda self: "RAW"
        self.senses['light']['all'] =   self.getLightRangeAll

        # location of sensors' hits:
        self.senses['light']['x'] = self.getIRXCoord
	self.senses['light']['y'] = self.getIRYCoord
	self.senses['light']['z'] = lambda self, pos: 0.03
	self.senses['light']['value'] = self.getLightRange
	self.senses['light']['flag'] = self.getIRFlag

	# location of origin of sensors:
        self.senses['light']['ox'] = self.light_ox
	self.senses['light']['oy'] = self.light_oy
	self.senses['light']['oz'] = lambda self, pos: 0.03 # meters
	self.senses['light']['th'] = self.light_th
        # in radians:
        self.senses['light']['arc'] = lambda self, pos, \
                                      x = (15 * math.pi / 180) : x

        self.senses['self'] = self.senses['robot']

        console.log(console.INFO,'khepera sense drivers loaded')

        self.controls['move'] = self._move
        self.controls['move_now'] = self._move_now
        self.controls['accelerate'] = self.accelerate
        self.controls['translate'] = self.translate
        self.controls['rotate'] = self.rotate
        self.controls['update'] = self.update 
        self.controls['localize'] = self.localize

        console.log(console.INFO,'khepera control drivers loaded')
        self.SanityCheck()

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
	self.update() 
        self.inform("Done loading robot.")

    def _draw(self, options, renderer): # overloaded from robot
        #self.setLocation(self.senses['robot']['x'], \
        #                 self.senses['robot']['y'], \
        #                 self.senses['robot']['z'], \
        #                 self.senses['robot']['thr'] )
        renderer.xformPush()
        renderer.color((0, 0, 1))
        #print "position: (", self.get('robot', 'x'), ",",  \
        #      self.get('robot', 'y'), ")"

        #renderer.xformXlate((self.get('robot', 'x'), \
        #                     self.get('robot','y'), \
        #                     self.get('robot','z')))
        renderer.xformRotate(self.get('robot', 'th'), (0, 0, 1))

        renderer.xformXlate(( 0, 0, .09))
        renderer.torus(.12, .12, 12, 24)

        renderer.color((.5, .5, .5))

        # wheel 1
        renderer.xformPush()
        renderer.xformXlate((0, .18, 0))
        renderer.xformRotate(90, (1, 0, 0))
        renderer.torus(.06, .06, 12, 24)
        renderer.xformPop()

        # wheel 2
        renderer.xformPush()
        renderer.xformXlate((0, -.18, 0))
        renderer.xformRotate(90, (1, 0, 0))
        renderer.torus(.06, .06, 12, 24)
        renderer.xformPop()

        # IR
        renderer.xformPush()
        renderer.color((0.7, 0, 0))
        for i in range(self.get('ir', 'count')):
            y1, x1, z1 = -self.get('ir', 'x', i), \
                         -self.get('ir', 'y', i), \
                         self.get('ir', 'z', i)
            y2, x2, z2 = -self.get('ir', 'ox', i), \
                         -self.get('ir', 'oy', i), \
                         self.get('ir', 'oz', i)
            #x2, y2, z2 = 0, 0, z1
            arc    = self.get('ir', 'arc', i) # in radians
            renderer.ray((x1, y1, z1), (x2, y2, z2), arc)

        renderer.xformPop()        

        # end of robot
        renderer.xformPop()

    def getIRXCoord(self, dev, pos):
        # convert to x,y relative to robot
        dist = self.rawToUnits(dev, self.senseData['ir'][pos], 'ir', 'METERS')
        angle = (-self.light_thd(dev, pos)  - 90.0) / 180.0 * math.pi
        return dist * math.cos(angle)
        

    def getIRYCoord(self, dev, pos):
        # convert to x,y relative to robot
        dist = self.rawToUnits(dev, self.senseData['ir'][pos], 'ir', 'METERS')
        angle = (-self.light_thd(dev, pos) - 90.0) / 180.0 * math.pi
        return dist * math.sin(angle)
    
    def light_ox(self, dev, pos):
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

    def light_oy(self, dev, pos):
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

    def light_thd(self, dev, pos):
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

    def getOptions(self): # overload 
        pass

    def connect(self):
        pass

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
                        print "khepera packet error: type=", data, "vals=", irs
            return self.senseData[data]
        
    def update(self):
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
        if self.currSpeed[0] != 0:
            err = abs(float(self.senseData['stall'][2])/float(self.currSpeed[0]) - 1)
            if err < .25:
                self.stallHistory[self.stallHistoryPos] = 1
        if self.currSpeed[1] != 0:
            err = abs(float(self.senseData['stall'][5])/float(self.currSpeed[1]) - 1)
            if err < .25:
                self.stallHistory[self.stallHistoryPos] = 1
        # ----------- end compute stall
        self.stallHistoryPos = (self.stallHistoryPos + 1) % self.stallHistorySize
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

    def getX(self, dev):
        return self.mmToUnits(self.x, self.senses['robot']['units'](dev))
    
    def getY(self, dev):
        return self.mmToUnits(self.y, self.senses['robot']['units'](dev))
    
    def getZ(self, dev):
        return 0
    
    def getTh(self, dev):
        return self.th

    def getThr(self, dev):
        return self.thr

    def getIRMaxRange(self, dev):
        return self.rawToUnits(dev, 60.0, 'ir')

    def getIRRange(self, dev, pos):
        return self.rawToUnits(dev, self.senseData['ir'][pos], 'ir')

    def getLightRange(self, dev, pos):
        return self.rawToUnits(dev, self.senseData['light'][pos], 'light')

    def getLightMaxRange(self, dev):
        return self.rawToUnits(dev, 200.0, 'light')

    def mmToUnits(self, mm, units):
        if units == 'MM':
            return mm
        elif units == 'CM':
            return mm / 100.0
        elif units == 'METERS':
            return mm / 1000.0
        elif units == 'ROBOTS':
            return mm / 60.0
        
    def rawToUnits(self, dev, raw, name, units = None):
        if units == None:
            units = self.senses[name]['units'](dev)
        if name == 'ir':
            maxvalue = 60.0
            mm = min(max(((1023.0 - raw) / 1023.0) * maxvalue, 0.0), maxvalue)
        elif name == 'light':
            maxvalue = 200.0
            mm = min(max((raw / 511.0) * maxvalue, 0.0), maxvalue)
        else:
            raise 'InvalidType', "Type is invalid"
        if units == "ROBOTS":
            return mm / 55.0 # khepera is 55mm diameter
        elif units == "MM":
            return mm
        elif units == "RAW":
            return raw 
        elif units == "CM":
            return mm / 100.0 # cm
        elif units == "METERS":
            return mm / 1000.0 # meters
        elif units == "SCALED":
            return mm / maxvalue
        else:
            raise 'InvalidType', "Units are set to invalid type"

    def getIRRangeAll(self, dev):
        vector = [0] * self.get('ir', 'count')
        for i in range(self.get('ir', 'count')):
            vector[i] = self.getIRRange(dev, i)
        return vector

    def getLightRangeAll(self, dev):
        vector = [0] * self.get('light', 'count')
        for i in range(self.get('light', 'count')):
            vector[i] = self.getLightRange(dev, i)
        return vector

    def getIRFlag(self, dev, pos):
        return 0

    def light_th(self, dev, pos):
        return self.light_thd(dev, pos) / 180.0 * math.pi
    
    def move_now(self, trans, rotate):
        """
        This is only neaded if there is an accelleration model.
        There currently isn't, so this not useful yet.
        """
        self._move_now(self, trans, rotate)
        self.update()

    def _move_now(self, dev, trans, rotate):
        left  = int((trans * dev.translateFactor - \
                     rotate * dev.rotateFactor))
        right  = int((trans * dev.translateFactor + \
                      rotate * dev.rotateFactor))
        self.currSpeed = [left, right]
        dev.sendMsg('D,%i,%i' % (left, right))
        self.update()

    def move(self, trans, rotate):
        self._move(self, trans, rotate)
        self.update()

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
        
    def _move(self, dev, trans, rotate):
        self.lastTranslate = trans
        self.lastRotate = rotate
        # FIX: do min/max here
        self.adjustSpeed()

    def accelerate(self, trans, rotate): # incr
        self.lastTranslate += trans
        self.lastRotate += rotate
        # FIX: do min/max here
        self.adjustSpeed()
        
    def translate(dev, value):
        dev.lastTranslate = value
        dev.adjustSpeed()
    
    def rotate(dev, value):
        dev.lastRotate = value
        dev.adjustSpeed()
    
    def localize(self, x = 0.0, y = 0.0, thr = 0.0):
        self.x = x
        self.y = y
        self.thr = thr
        self.th = self.thr * (180.0 / math.pi)
    
if __name__ == '__main__':
    x = KheperaRobot()
    x.update()
    x.GetMin()
