from os import getenv

def pyrodir():
    return getenv("PYRO")

def startup_check():
    return pyrodir() != None
