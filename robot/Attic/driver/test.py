#
#
# This is a test driver(s) that does nothing interesting
# It has two senses:
#    'euler' who's reading is always euler's constant
#    'random' who's reading is a normalized
#             random vector in R3 that wanders around in a random walk
#
#
# TODO:
#   figure out how to put a python thread to sleep so that the random
#   walk computation will be at like 10 steps per sec isnted of constantly
#
# - stephen -
# 

import math
import thread
import random
import pyro.robot.driver as driver #??
import pyro.gui.console as console
import pyro.geometry as geometry

class TestSenseDriver(driver.Driver):
    def monitor(self):
        while 1:
            self.senses['random'].reading[0] += random.random()/100
            self.senses['random'].reading[1] += random.random()/100
            self.senses['random'].reading[2] += random.random()/100
            self.senses['random'].reading = [geometry.normalize(self.senses['random'].reading)]
            
    def __init__(self):
        driver.Driver.__init__(self)
        self.senses['euler'] = driver.Sense(
                                           [geometry.AffineVector()],
                                           [math.e])
        
        self.senses['random'] = driver.Sense([geometry.AffineVector()],
                                            [geometry.normalize([random.random(),
                                                                random.random(),
                                                                random.random()])]
                                 )
        thread.start_new_thread(self.monitor,())
        console.log(console.INFO,'test driver loaded')

class TestControlDriver(driver.Driver):
    def __init__(self):
        driver.Driver.__init__(self)
        self.controls['print'] = driver.Control(0)
        thread.start_new_thread(self.monitor,())
        

    def monitor(self):
        oldval = self.controls['print'].value
        while 1:
            if oldval != self.controls['print'].value:
                oldval = self.controls['print'].value
                print "TestControlDriver :   recieved value ",oldval
