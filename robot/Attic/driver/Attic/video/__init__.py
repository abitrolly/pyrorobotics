#
# This is the video 4 linux driver.
#
#
#
# - stephen -
#

from pyro.robot.driver import *
import pyro.gui.console as console
import low_video


class VideoSense(Sense):
    def __init__(self,fd,xres,yres):
        self.fd = fd
        self.xres = xres
        self.yres = yres
        self.size = xres*yres*3

    def getValue(self):
        return fd.read(self.size*3)
    
def getVideoDriverDefaults():
    vidopts = {}
    vidopts['name'] = 'camera'
    vidopts['device'] = '/dev/video'
    vidopts['xres'] = 160
    vidopts['yres'] = 120
    return vidopts

class VideoDriver(Driver):
    def __init__(self,options):
        Driver.__init__(self)
        console.log(console.INFO,'loading video driver')
        for vidopt in options:
            try:
                fd = open(vidopt['device'])
                err = low_video.setPrefs(fd.fileno(),vidopt['xres'],vidopt['yres'])
                if err != 0:
                    raise IOError
                try:
                    self.senses[vidopt['name']]
                    console.log(console.WARNING,'Duplicate VideoSensors created')
                except KeyError:
                    pass
                self.senses[vidopt['name']] = VideoSense(fd,vidopt['xres'],vidopt['yres'])
                
            except IOError:
                console.log(console.WARNING,'Could not open video device. Options specified: '+str(vidopt))

