#
#    Class to handle incoming messages from the Khepera-Robot
#   =============================================================
#
#   Author: Dr. Peter Stoehr        peter@peter-stoehr.de
#   Version:    July 1999 DPS
#               Small changes for the Khepera workshop
#
#               May-June 1997 DPS
#               First version
#               

########################################################################

from string import *

########################################################################

import Command
#import ConsoleCommand

########################################################################

class IRSensorCommand(Command.Command):
    """
    Parent class that is able to handle the messages releated to the
    proximity and ambient light messages
    """
 
    def action(self, aString):
        """
        Decompose the ASCII-based representation of the message and
        store the info as integer values
        """
        vAfterKomma = find(aString, ",") + 1
        self.mValues = self._String2NumArray(aString, vAfterKomma, 8)

########################################################################

class ProximitySensorCommand(IRSensorCommand):
    """
    Derived class from IRSensorCommand class that handles the message
    containing the data of the proximity sensors
    """
    def action(self, aString):
        # Call base class method to decompose message
        IRSensorCommand.action(self, aString)
        # Display the data
        #self.mWidget.displayProximity(self.mValues)

########################################################################

class AmbientLightCommand(IRSensorCommand):
    """
    Derived class from IRSensorCommand class that handles the message
    containing the data of the ambient light sensors
    """
    def action(self, aString):
        # Call base class method to decompose message
        IRSensorCommand.action(self, aString)
        # Display the data
        #self.mWidget.displayAmbient(self.mValues)

########################################################################

class WheelPositionCommand(Command.Command):
    """
    Handle the message containing the wheels position
    """

    def action(self, aString):
        vAfterKomma = find(aString, ",") + 1
        # Decompose the ASCII-based representation of the message and
        # store the info as integer values
        vValues = self._String2NumArray(aString, vAfterKomma, 2)

        # Display the data
        #self.mWidget.displayPosition(vValues[0], vValues[1])
