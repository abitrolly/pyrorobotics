from pyro.camera.blob import *

def INIT(robot):
    return {"BlobCamera": BlobCamera(robot)}
