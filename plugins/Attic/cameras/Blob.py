from pyro.camera.blob import *

def INIT(engine):
    return BlobCamera(engine.robot)
