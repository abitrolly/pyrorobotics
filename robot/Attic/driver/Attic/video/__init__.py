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
    def __init__(self, fd, xres, yres, depth = 3):
        self.fd = fd
        self.depth = depth
        self.xres = xres
        self.yres = yres
        self.size = xres*yres*depth
        
    def getValue(self):
        return self.fd.read(self.size)
    
def getVideoDriverDefaults():
    """ A default dictionary of some standard values. """
    vidopts = {}
    vidopts['name'] = 'camera'
    vidopts['device'] = '/dev/video0'
    vidopts['xres'] = 160
    vidopts['yres'] = 120
    return vidopts

class VideoDriver(Driver):
    def __init__(self, options):
        Driver.__init__(self)
        console.log(console.INFO,'loading video driver')
        # for each camera:
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
                
if __name__ == '__main__':
    # send in a list of cameras:
    vd = VideoDriver([getVideoDriverDefaults()])
    print vd.senses['camera'].getValue()
