#
#    Definition of the generic Command class to handle preprocessed 
#    commands sent from the robot to the programm
#
#   Author: Dr. Peter Stoehr        peter@peter-stoehr.de
#   Version:    July 1999 DPS
#               Small changes for the Khepera workshop
#
#               April-June 1997 DPS
#               First version
#               
#

from string import *

########################################################################

class Command:
    """
    Command defines the generic class to handle preprocessed commands
    send by the robot.
    An instance of class Command (or of a dereived class) is called
    used as a callback by the dispatcher (or a dereived class) to handle
    a specific return string
    """
    
    def __init__(self, aWidget = ''):
        # Store the widget the output should be sent to
        #self.mWidget = aWidget
        pass

    ####################################################################

    def action(self, aString):
        """
        This method is called by the dispatcher to display the content
        of the encoded message stored in aString.
        The default action is to call the display method of the widget
        """
        #self.mWidget.display(aString)
        print "Command Display: %s" % aString

    ####################################################################

    def _String2NumArray(self, aString, aStartInd, aNr, aDelimiter=","):
        """
        Private method used to decompose a message containing numeric
        values and to store the numeric representations in an array
        and return it to the caller.
        Decoding starts at the index aStartInd. 
        It is assumed that aNr numeric values are encoded in the string.
        If more or less values can be found, a ValueError exception is 
        generated.
        The numeric values should be seperated by the delimiter aDelimiter.
        """
        
        vValues = {}
        vBeginInd = aStartInd
        
        # Values found up to now
        vCnt = 0
        
        while 1:
            try:
                # Decompose the string to find the next item
                vNextInd = index(aString, aDelimiter, vBeginInd)
            except ValueError:
                # No delimiter found --> last value encoded in the string
                vValues[vCnt] = atoi(aString[vBeginInd:])
                break
            else:
                # Delimiter found, decompose the string
                vValues[vCnt] = atoi(aString[vBeginInd:vNextInd])
                # Store index of delimiter for the next search
                vBeginInd = vNextInd + 1
                
            # One more value found
            vCnt = vCnt + 1

        # Check if the correct amount of data was found
        if (vCnt + 1 <> aNr):
            print "Should have been:", (vCnt + 1), "=", aNr
            raise ValueError

        # return the array with elements found
        return vValues
                
########################################################################

class NullCommand(Command):
    """
    Command that does throws away the string sent by the robot
    """
    def action(self, aString):
        pass
