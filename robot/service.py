class Service:
    """ A basic service class """

    def __init__(self):
        self.active = 1
        self.visible = 0
        self.state = "stopped"

    def startService(self):
        self.state = "started"
        return "Ok"

    def stopService(self):
        self.state = "stopped"
        return "Ok"

    def makeWindow(self):
        raise "NoServiceWindowDefined"

    def updateWindow(self):
        raise "NoServiceWindowDefined"

    def getServiceData(self):
        return {}

    def getServiceState(self):
        return self.state

    def update(self):
        pass
