# Camera class

import os
from pyro.vision import PyroImage

class Camera:
"""
A base class for Camera
"""


    def __init__(self, width, height, depth = 3):
    """
    To specify the resolution of a particular camera, overload this
    constructor with one that initalizes the dimensions itself
    """
        self.width = width
        self.height = height
        self.depth = depth

    def update(self):
    """
    Return a PyroImage from the camera.  This method should be
    overloaded to interface with the actual camera.
    """
        img = PyroImage(self.width, self.height, self.depth, 0)
        
        return img
