
class WindowError(AttributeError):
    """ Service Window Error """

class ServiceError(AttributeError):
    """ Used to signal service problem """

class Service:
    """ A basic service class """

    def __init__(self, serviceType = 'basic', visible = 0):
        self.active = 1
        self.visible = visible
        self.dev = 0
        self.type = serviceType
        self.state = "stopped"
        if visible:
            self.makeWindow()

    def startService(self):
        self.state = "started"
        return self

    def stopService(self):
        self.state = "stopped"
        return "Ok"

    def makeWindow(self):
        raise WindowError, "No Service Window Defined"

    def updateWindow(self):
        raise WindowError, "No Service Window Defined"

    def getServiceData(self):
        return {}

    def getServiceState(self):
        return self.state

    def updateService(self):
        pass
