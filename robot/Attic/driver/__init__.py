#
#
# driver interface
#
# TODO:
#  Add cleanup (shutdown())
#
# - stephen -
#

import pyrobot.gui.console as console

class Sense:
    def __init__(self,geometry,reading):
        """ this should construct the sence. duh. """
        self.geometry = geometry
        self.reading = reading
    def getGeometry(self):
        """
        returns a LIST of AffineVectors that represent the geometry of the
        values returned in getValue. The ordering determines the coorespondance.
        If this does not make sence (i.e. odomoter) return an empty list.
        """
        return self.geometry
    def getValue(self):
        """
        returns an array of values cooresponding to the sensor's readings.
        the specific type is dependant on the sensor and is understood by
        above layer by semantics of use. (If i ask for a range sensor i know
        that i am getting back a vector of scalars representing the distance
        to the reflection of the sensing media.)
        """
        return self.reading

class RangeSense(Sense):
    def getHit(self):
        a = []
        #for v in self.getGeometry():
        #    a.append(scalar(self.getGeometry(),self.getValue()))
        return a

    def getAngle():
        return 0

    def getReliability():
        return 0

    def setResolution():
        pass

class AudioSense(Sense):
    def getWave(length):
        return 0
    def getWave():
        return 0
    def getNoiseLevel():
        return 0
    def getAudioProperties():
        return 0
    def setResolution():
        pass

class ImageSense(Sense):
    def getImage():
        return 0
    def setResolution():
        return 0

class Control:
    """
    a control sensor.
    """
    def __init__(self,value):
        """
        the data type of value is semanticly defined.
        """
        self.value = value
        
    def setValue(self,value):
        self.value = value
    def getValue(self):
        return self.value

class Driver:
    """
    simple enough eh?
    """
    def __init__(self):
        self.senses = {}
        self.controls = {}
          
    def getSenses(self):
        return self.senses;

    def getControls(self):
        return self.controls
    
    def shutdown(self):
        pass
