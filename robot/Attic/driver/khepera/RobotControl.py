#
#    Class with messages to invoke commands at the Khepera robot
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


class RobotControl:
    """
    Abstract interface to the Khepera robot
    Errors (for example timeouts or any other strang things) are reported
    via exceptions and have to be handled by the caller. 
    """
    
    def __init__(self, aConnection):
        self.mConnection = aConnection

    ####################################################################

    def sendMsg(self, aString):
        """ 
        Send a string message to the Khepera Robot
        """
        self.mConnection.writeline(aString)

    ####################################################################

    def loadProgramm(self, aFileName):
        """
        Send the s28 file to the Khepera robot
        """

        vFile = open(aFileName,"r")
        vPrg = vFile.readlines()
        vFile.close()
        self.mConnection.writeblock(vPrg)
        del vPrg
        

    ####################################################################
    #
    # The methods below send the appropriated ASCII-command-strings to
    # the Khepera computer.
    # 
    ####################################################################


    def moveTo(self, aLeft, aRight):
        vString = "C," + str(aLeft) + "," + str(aRight)
        self.sendMsg(vString)

    ####################################################################

    def getPosition(self):
        self.sendMsg("H")

    ####################################################################

    def getProximity(self):
        self.sendMsg("N")

    ####################################################################

    def getAmbient(self):
        self.sendMsg("O")

    ####################################################################

    def getCameraPic(self):
        self.sendMsg("T,2,N")

    ####################################################################

    def getCameraIntensity(self):
        self.sendMsg("T,2,L")

    ####################################################################

    def getCameraMin(self):
        self.sendMsg("T,2,P")

    ####################################################################

    def getCameraMax(self):
        self.sendMsg("T,2,O")

    ####################################################################

    def getCameraLowRes(self):
        self.sendMsg("T,2,M")

    ####################################################################

    def getCamera2Sub(self):
        self.sendMsg("T,2,S")

    ####################################################################

    def getCamera4Sub(self):
        self.sendMsg("T,2,T")

    ####################################################################

    def setCameraScanningPeriod(self, aPeriodID):
        vString = "T,2,U," + str(aPeriodID)
