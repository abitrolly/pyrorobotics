#
#    Class to handle incoming messages from the K213 vision turret
#   ===============================================================
#
#   Author: Dr. Peter Stoehr        peter@peter-stoehr.de
#
#   Version:    July 1999 DPS
#               Small changes for the Khepera workshop
#
#               May-June 1997 DPS
#               First version
#               

########################################################################

from string import *

import Command
#import ConsoleCommand
import CommandDispatcher

########################################################################

class CameraCommand(Command.Command):
    """
    This class uses an own instance of the dispatcher pattern to handle
    the incoming camera messages.
    """
 
    def __init__(self, aWidget, aDefaultHandler):
        Command.Command.__init__(self, aWidget)
        self.mDefaultHandler = aDefaultHandler
        # Create the dispatcher
        self.mCameraDispatcher = CommandDispatcher.CommandDispatcher()
        # Add the actions to the dispatcher
        self._addActions()

    ####################################################################
        
    def _addActions(self):

        # The desfault action is to display the string in the console
        # widget
        self.mCameraDispatcher.addDefaultReceiver(self.mDefaultHandler)

        # Handle incoming 8 pixel wide sub-images
        self.mRead8 = ReadSmallImageCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,q", self.mRead8)

        # Handle incoming 16 pixel wide sub-images
        self.mRead16 = ReadSmallImageCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,r", self.mRead16)

        # Handle incoming 2 times sub-sampled picture
        self.mReadSub2 = ReadSub2ImageCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,s", self.mReadSub2)

        # Handle incoming 4 times sub-sampled picture
        self.mReadSub4 = ReadSub4ImageCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,t", self.mReadSub4)

        # Handle incoming picture with 4 bit resolution
        self.mReadLowRes = ReadLowResImageCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,m", self.mReadLowRes)

        # Handle incoming standard picture 
        self.mReadImage = ReadImageCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,n", self.mReadImage)

        # Handle incoming message which returns the intensity measured
        self.mReadIntensity = ReadIntensityCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,l", self.mReadIntensity)

        # Handle incoming message returning the index of the brightest pixel
        self.mReadMax = ReadMaxCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,o", self.mReadMax)

        # Handle incoming message returning the index of the darkest pixel
        self.mReadMin = ReadMinCommand(self.mWidget)
        self.mCameraDispatcher.addReceiver("t,2,p", self.mReadMin)

    ####################################################################

    def action(self, aString):
        """
        Callback that is called by the top-level dispatcher as soon as
        a message with the prefix 't,2,' is detected
        """

        # Call second-level dispatcher to handle the camera command
        self.mCameraDispatcher.dispatch(aString)


########################################################################


class ReadImageCommand(Command.Command):
    """
    Class that contains the action to handle incoming messages with
    a standard picture.
    """

    def action(self, aString):
        # Index of the first data entry
        vAfterKomma = len("t,2,n,")
        # Translate the string-representation of the pixel-picture
        # in a integer representation
        vValues = self._String2NumArray(aString, vAfterKomma, 64)

        # Call the display routine of the Camera-Widget
        self.mWidget.display(vValues)


########################################################################


class ReadLowResImageCommand(Command.Command):
    """
    Class that contains the action to handle incoming messages with
    a low resolution picture.
    """

    def action(self, aString):
        # Index of the first data entry
        vAfterKomma = len("t,2,m,")
        # Translate the string-representation of the pixel-picture
        # in a integer representation
        vValues = self._String2NumArray(aString, vAfterKomma, 32)

        vGrayValues = {}
        
        # Transform the 4 bit pixel image in a 8 bit one
        for i in range(32):

            # Decompose an entry into the lower and the upper 4 bits and
            # make a 8 bit value
            vHighNibble = vValues[i] & 0xF0
            vLowNibble  = (vValues[i] & 0x0F) * 16

            # Store these values in a intermediate array
            vBase = i * 2
            vGrayValues[vBase] = vHighNibble
            vGrayValues[vBase+1] = vLowNibble

        # Call the display routine of the Camera-Widget with the 
        # transformed data
        self.mWidget.display(vGrayValues)

########################################################################

class ReadSub2ImageCommand(Command.Command):
    """
    Class that contains the action to handle incoming messages with
    a two times sub-sampled image
    """

    def action(self, aString):
        # Index of the first data entry
        vAfterKomma = len("t,2,s,")
        # Translate the string-representation of the pixel-picture
        # in a integer representation
        vValues = self._String2NumArray(aString, vAfterKomma, 32)

        vGrayValues = {}

        # Translate the 2 times sub-sampled image in a standard image
        # just by copying every pixel two times to the intermediate
        # pixel picture
        for i in range(32):
            vBase = i * 2
            vGrayValues[vBase] = vValues[i]
            vGrayValues[vBase+1] = vValues[i]
                    
        # Call the display routine of the Camera-Widget with the 
        # transformed data
        self.mWidget.display(vGrayValues)

########################################################################

class ReadSub4ImageCommand(Command.Command):
    """
    Class that contains the action to handle incoming messages with
    a four times sub-sampled image
    """

    def action(self, aString):
        # Index of the first data entry
        vAfterKomma = len("t,2,t,")
        # Translate the string-representation of the pixel-picture
        # in a integer representation
        vValues = self._String2NumArray(aString, vAfterKomma, 16)

        vGrayValues = {}

        # Translate the 4 times sub-sampled image in a standard image
        # just by copying every pixel two times to the intermediate
        # pixel picture
        for i in range(16):
            vBase = i * 4
            vGrayValues[vBase] = vValues[i]
            vGrayValues[vBase+1] = vValues[i]
            vGrayValues[vBase+2] = vValues[i]
            vGrayValues[vBase+3] = vValues[i]
                    
        # Call the display routine of the Camera-Widget with the 
        # transformed data
        self.mWidget.display(vGrayValues)


########################################################################


class ReadSmallImageCommand(Command.Command):
    """
    Handle messages of 8 or 16 pixel wide sub images
    """

    def action(self, aString):
        # Index of the first data entry
        vAfterKomma = len("t,2,x,")

        # Check if we have to handle 8 or 16 pixel wide images
        if (aString[4] == "q"):
            vMax = 8
        else:
            vMax = 16

        # Translate the ASCII data in numeric data
        vValues = self._String2NumArray(aString, vAfterKomma, vMax)

        # Fill-up the intermediate array with "No-Value" info
        for i in range(vMax,64):
            vValues[i] = -1

        # Call the display routine of the Camera-Widget with the 
        # transformed data
        self.mWidget.display(vValues)


########################################################################


class ReadIntensityCommand(Command.Command):
    """
    Handle an incoming string the contains the info about the
    intensity measured by the camera
    """
    def action(self, aString):
        # Decompose the message
        vAfterKomma = len("t,2,l,")
        vValues = self._String2NumArray(aString, vAfterKomma, 2)

        # Call appropriated display-routine
        self.mWidget.displayIntensity(vValues[0], vValues[1])


########################################################################


class ReadMinMaxCommand(Command.Command):
    """
    Handle an incoming string the contains either the info about the
    index of the brightest or the darkest pixel.
    Abstract class ...
    """
    def action(self, aString):
        vAfterKomma = len("t,2,X,")
        vValue = atoi(aString[vAfterKomma:-1])
        self._doCall(vValue)

    def _doCall(self, aValue):
        pass

# ----------------------------------------------------------------------

class ReadMinCommand(ReadMinMaxCommand):
    """
    Specialisation of ReadMinMAxCommand to handle info about the the
    index of the darkest pixel
    """
    def _doCall(self, aValue):
        self.mWidget.displayMin(aValue)

# ----------------------------------------------------------------------

class ReadMaxCommand(ReadMinMaxCommand):
    """
    Specialisation of ReadMinMAxCommand to handle info about the the
    index of the brightest pixel
    """
    def _doCall(self, aValue):
        self.mWidget.displayMax(aValue)


