class Service:
    """ A basic service class """

    def __init__(self):
        self.visible = 0

    def start(self):
        print "Starting service..."

    def stop(self):
        print "Stopping service..."

    def makeWindow(self):
        print "Making window..."

    def updateWindow(self):
        print "Updating window..."
