from os import getenv

def pyrobotdir():
    return getenv("PYROBOT")

def startup_check():
    return pyrobotdir() != None
