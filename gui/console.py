# pyro.gui.console
#
# This is a text output facility for the xrcl base.
# it is modeled after the normal syslog(3) 
#
# It is pretty simple.
#

#verbosity levels
FATAL   = 0
ERROR   = 1
WARNING = 2
INFO    = 3
DEBUG   = 4

#verbosity strings
verbosityMessage = ["fatal","error","warning","info","debug"]

verbosityLevel = 4

def log(level, message):
    if level <= verbosityLevel:
        print verbosityMessage[level],": ",message
    if level == 'fatal':
        raise message

def setVerbosity(level):
    verbosityLevel = level

