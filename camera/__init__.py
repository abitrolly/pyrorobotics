# Camera class

import os

class Camera:

    def snap(self, filename = 'camera.ppm'):
        print "Capturing image '%s'..." % filename
        os.system("bttvgrab -G /dev/video0 -f %s -o pgm -N NTSC -Q -l 1 -S 1 -d q -W 32 -w 48" % filename)
