#
#    Config file for the serial interface definiton
#   ================================================
#
#   Author: Dr. Peter Stoehr        peter@peter-stoehr.de
#
#               May-June 1997 DPS
#               First version
#               

########################################################################

import termios

########################################################################

# Define the baud-rate 
#   9600 Baud use   TERMIOS.B9600
#  19200 Baud use   TERMIOS.B19200
#  38400 Baud use   TERMIOS.B38400
gBaudRate = termios.B38400

# Define the name of the device to be used to open the seriell interface
gTTY = "/dev/ttyS1"
