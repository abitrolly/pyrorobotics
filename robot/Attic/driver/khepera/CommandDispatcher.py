#
#    Class for handling incoming requests from the serial line
#   ===========================================================
#
#   Author: Dr. Peter Stoehr        peter@peter-stoehr.de
#   Version:    July 1999 DPS
#               Small changes for the Khepera workshop
#
#               May-June 1997 DPS
#               First version
#               

########################################################################

import string

########################################################################

class CommandDispatcher:
    """
    This class implements a simple dispatcher for incoming ASCII-messages.
    """

    def __init__(self):
        self.mDefault = None
        self.mDispatcher = {}
        
    ########################################################################

    def addReceiver(self, aPrefix, aAction):
        """
        Add the function aAction that is called whenever a string with
        the prefix aPrefix is checks by the dispatcher
        """
        self.mDispatcher[aPrefix] = aAction
    
    ########################################################################

    def addDefaultReceiver(self, aDefault):
        """ 
        The action aDefault is called if none of the registered prefixes
        match the incoming message.
        """
        self.mDefault = aDefault

    ########################################################################

    def dispatch(self, aString):
        """
        Interface to the 'real' dispatching algorithm.
        For every \n terminated substring of aString the appropriated
        actions is searched and called afterwards
        """

        # Decompose the string
        vStrings = string.split(aString, "\n")
        self.notdone = 1
        # For every substring call the dispatching algorithm
        for vString in vStrings:
            self._doDispatch(vString)
        if self.notdone:
            print "Didn't do anything!"

    # ------------------------------------------------------------------
    
    def _doDispatch(self, aString):
        """
        Dispatching algorithm.
        1) Return if string is empty
        2) Extract the prefixes from the dictionary 
        3) Compare each prefix with the begin of the message
        4) If we find a match call the registered function
        5) If no match is found call default
        """

        if string.strip(aString) == "":
            return

        for vPrefix in self.mDispatcher.keys():
            vLen = len(vPrefix)
            if (vPrefix == aString[:vLen]):
                vHandler = self.mDispatcher[vPrefix]
                vHandler.action(aString)
                self.notdone = 0
                return

        if (self.mDefault):
            print "Doing default action"
            self.mDefault.action(aString)
