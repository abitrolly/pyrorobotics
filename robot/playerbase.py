# Defines PlayerRobot, a subclass of robot

from pyro.robot import *
from math import pi, cos, sin
from os import getuid
from pyro.robot.driver.player import *
import random, time

PIOVER180 = pi / 180.0
DEG90RADS = 0.5 * pi
COSDEG90RADS = cos(DEG90RADS) / 1000.0
SINDEG90RADS = sin(DEG90RADS) / 1000.0

class PlayerBase(Robot):
    def __init__(self, name = "Player", port = 6665):
        Robot.__init__(self, name, "player") # robot constructor
        self.simulated = 1
        self.port = port
        self.inform("Loading Player robot interface...")
        self.name = name
        self.connect()
        # default values
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.thr = 0.0
        self.stall = 0
        self.messages = []
        self.noise = .2 # 20 % noise
        
    def translate(self, translate_velocity):
        self.translateDev(self.dev, translate_velocity)

    def translateDev(self, dev, translate_velocity):
        self.update()
        dev.set_speed(translate_velocity * 1100.0, None, None)

    def rotate(self, rotate_velocity):
        self.rotateDev(self.dev, rotate_velocity)

    def rotateDev(self, dev, rotate_velocity):
        self.update()
        dev.set_speed(None, None, rotate_velocity * 75.0)

    def move(self, translate_velocity, rotate_velocity):
        self.moveDev(self.dev, translate_velocity, rotate_velocity)

    def moveDev(self, dev, translate_velocity, rotate_velocity):
        self.update()
        dev.set_speed(translate_velocity * 1100.0,
                      0,
                      rotate_velocity * 75.0)

    # FIX: either sonar values are changing between calls to X, Y
    # or sin/cos values are not taking into account offset from center
        
    def localXDev(self, dev, pos):
        thr = (self.sonarGeometry[pos][2] + 90.0) * PIOVER180
        dist = self.rawToUnits(dev, self.dev.sonar[0][pos], 'sonar')
        x = self.rawToUnits(dev, self.sonarGeometry[pos][0], 'sonar')
        return cos(thr) * dist

    def localYDev(self, dev, pos):
        thr = (self.sonarGeometry[pos][2] - 90.0) * PIOVER180
        dist = self.rawToUnits(dev, self.dev.sonar[0][pos], 'sonar')
        y = self.rawToUnits(dev, self.sonarGeometry[pos][1], 'sonar') 
        return sin(thr) * dist

    def getX(self, dev):
        return self.x

    def getY(self, dev):
        return self.y
    
    def getZ(self, dev):
        return self.z
    
    def getTh(self, dev):
        return self.th
    
    def getThr(self, dev):
        return self.thr

    def update(self):
        self.updateDev(self.dev)
    
    def updateDev(self, dev):
        data = dev.get_position()
        pos, speeds, stall = data
        # (xpos, ypos, th), (xspeed, yspeed, rotatespeed), stall
        self.x = pos[0] / 1000.0
        self.y = pos[1] / 1000.0
        self.th = pos[2] # degrees
        self.thr = self.th * PIOVER180
        self.stall = stall
        try:
            if self.dev.comms[0] != '':
                for i in self.dev.comms:
                    self.messages.append(self.dev.get_comms())
        except:
            # comms interface not on
            pass
        
    def getOptions(self): # overload 
        pass

    def disconnect(self):
        print "Disconnecting..."

    def rawToUnits(self, dev, raw, name):
        raw = raw / 1000.0
        if self.noise > 0:
            if random.random() > .5:
                raw += (raw * (self.noise * random.random()))
            else:
                raw -= (raw * (self.noise * random.random()))
                
        if name == 'sonar':
            val = min(max(raw, 0.0), 2.99)
        else:
            raise 'InvalidType', "Type is invalid"
        if self.senses[name]['units'](dev) == "ROBOTS":
            return val / 0.75 # Pioneer is about .5 meters diameter
        elif self.senses[name]['units'](dev) == "MM":
            return val * 1000.0
        elif self.senses[name]['units'](dev) == "CM":
            return (val) * 100.0 # cm
        elif self.senses[name]['units'](dev) == "METERS" or \
                 self.senses[name]['units'](dev) == "RAW":
            return (val) 
        elif self.senses[name]['units'](dev) == "SCALED":
            return val / 2.99
        else:
            raise 'InvalidType', "Units are set to invalid type"

    def sendMessage(self, message):
        if self.dev.comms == {}:
            print "Need to startService 'comms' interface in robot"
            return
        self.dev.send_message(message)

    def getMessages(self):
        if not 'comms' in dir(self.dev) or self.dev.comms == {}:
            raise "Need to startService 'comms' interface in robot"
        if self.dev.comms[0] != '':
            self.update()
        tmp = self.messages
        # reset queue:
        self.messages = []
        return tmp

    def startService(self, item):
        self.dev.start(item)
        print "Starting service '%s'..." % item
        time.sleep(1)

    def stopService(self, item):
        self.dev.stop(item)

    def hasService(self, item):
        return item in dir(self.dev) and self.dev.__dict__[item] != {}

    def getServiceData(self, item):
        return self.dev.__dict__[item][0]

    # Gripper functions
    #these also exist: 'gripper_carry', 'gripper_press', 'gripper_stay',

    def gripperOpen(self):
        return self.dev.gripper_open() 

    def gripperClose(self):
        return self.dev.gripper_close() 

    def gripperStop(self):
        return self.dev.gripper_stop()

    def liftUp(self):
        return self.dev.gripper_up()

    def liftDown(self):
        return self.dev.gripper_down()

    def liftStop(self):
        return self.dev.gripper_stop()

    def gripperStore(self):
        return self.dev.gripper_store() 

    def gripperDeploy(self):
        return self.dev.gripper_deploy()

    def gripperHalt(self):
        return self.dev.gripper_halt()

    def getGripperState(self):
        return self.dev.is_paddles_closed() # help!

    def getBreakBeamState(self):
        sum = 0
        sum += self.dev.is_ibeam_obstructed() * 2 #FIX: which?
        sum += self.dev.is_obeam_obstructed()
        return sum

    def isGripperClosed(self): # FIX: add this to aria
        return self.dev.is_paddles_closed() #ok

    def isGripperMoving(self):
        return self.dev.is_paddles_moving() #ok

    def isLiftMoving(self):
        return self.dev.is_lift_moving() # ok

    def isLiftMaxed(self):
        return self.dev.is_lift_up() # ok
    
if __name__ == '__main__':
    myrobot = PlayerBase()
    myrobot.update()
    #myrobot.translate(.2)
    #myrobot.translate(.0)
    #myrobot.disconnect()
