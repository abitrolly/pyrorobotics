from os import getenv

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"


def pyrobotdir():
    return getenv("PYROBOT")

def startup_check():
    return pyrobotdir() != None

