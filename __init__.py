import os

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "5.0.4"

def pyrobotdir():
    return os.path.split(os.path.abspath(__file__))[0]

def startup_check():
    return pyrobotdir() != None

