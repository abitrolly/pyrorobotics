import time
import StringIO
import os
import select
import Queue
from threading import *

import SerialConnection
import CommandDispatcher
import RobotControl
from Configure import *
import Command
import KheperaCommand
import CameraCommand
import Camera

########################################################################

class monitorSerialIO(Thread):
    """
    Thread used to monitor the serial IO interface
    """
    
    def __init__(self, aPipe, aQueue, aSerialIO):
        Thread.__init__(self)
        self.mPipe = aPipe
        self.mQueue = aQueue
        self.mSerialIO = aSerialIO
        # Create a "daemon" to handle unsolicited exit requests
        Thread.setDaemon(self,1)

    def run(self):
        """
        Thread main-routine 
        """
        while 1:
            # Wait for data at the serial interface
            vString = self.mSerialIO.readline(aBlocking=1)
            # Store received data in a global queue 
            self.mQueue.put(vString)
            # Send token to main-thread -> data was received
            self.mPipe.write("t\n")
            self.mPipe.flush()
    
        
########################################################################

def getSerialParameters():
    """
    Procedure to handle user-defintions of the serial interface.
    This is done using two environment variables:
        1) PyKhep_Baud to set the baud-rate (values have to conform
           to the values defined in TERMIOS 
        2) Name of the device
    The data is stored in the global config parameters gBaudRate and 
    gTTY. These values are predefined in the Configure.py file.
    """
    global gBaudRate, gTTY
    from TERMIOS import *

    try:
        vString = os.environ["PyKhep_Baud"]
    except KeyError:
        pass
    else:
        vCommand = "gBaudRate = %s" % (vString)
        exec(vCommand)

    try:
        vString = os.environ["PyKhep_TTY"]
    except KeyError:
        pass
    else:
        gTTY = vString

########################################################################

def pipeCallback(file, mask):
    """
    Callback trigger by Tkinter as soon as we have some new data stored
    in the interconnecting pipe. The pipe is used to send a token 
    that indicates that some data was read from the serial interface
    and stored in the globale message queue
    """
    
    global gDispatcher, gQueue

    # Read the token from the pipe.
    vDummy = readAllLines(file)
    
    while 1:
        # Read an item from the queue
        try:
            vString = gQueue.get(0)
        except Queue.Empty:
            # Queue was empty --> leave
            break
        try:
            # Handle the string received from the robot
            # First step, call the top-level command dispatcher
            gDispatcher.dispatch(vString)
        except ValueError:
            # If an error occured send a message via the dispatcher
            # to the Khepera-Console widget
            vErrorMsg = 'Can not handle the command string: ' + vString 
            gDispatcher.dispatch(vErrorMsg)

########################################################################

def go():
    global gDispatcher, gQueue

    # Check for user settings
    getSerialParameters()
    # Create a serialIO connection 
    sc = SerialConnection.SerialConnection(gTTY, gBaudRate)

    # Create the queue used to send infos from the serialIO thread to the
    # main thread
    gQueue = Queue.Queue(256)

    # Pipes for token-passing
    (vFileR, vFileW) = os.pipe()
    reader = os.fdopen(vFileR, "rb", 256)
    writer = os.fdopen(vFileW, "wb", 256)

    # Create an instance capable to send messages to the robot
    gControl = RobotControl.RobotControl(sc)


    # Widget to display textual messages
    # gConsoleWidget = KhepConsole.KhepConsole(gRoot)
    # Widget for the K213 turret
    # gCameraWidget  = Camera.KheperaCamera(gRoot, gControl)

    # List containg infos about additionl widgets used for the turrets
    # Structure of an entry
    # 1) Menue entry used to invoke the widget
    # 2) String for on-line help
    # 3) Proc to be called to invoke the widget
    #vWidgets = [
    #("Console widget", "Console widget", gConsoleWidget.showWindows),
    #("K213 Camera display", "K213 Vision Turret", gCameraWidget.showWindows)
    #]
    
    # Standard Khepera-widget
    # gKheperaWidget = KheperaDiagramm.KheperaDiagramm(gRoot, gControl)
    # Add widgets for the turrets
    #gKheperaWidget.addWidgets(vWidgets)
    
    # Create the global command dispatcher
    gDispatcher = CommandDispatcher.CommandDispatcher()
    
    # Create a class able to handle messages sent to the console widget
    #gConsoleAction = ConsoleCommand.ConsoleCommand(gConsoleWidget)
    
    # Create classes able to handle messages with proximity data, ambient light
    # sensor data and the robot position
    # Output widget is the standard Khepera-widget
    gProximityAction = KheperaCommand.ProximitySensorCommand() # gKheperaWidget)
    #gAmbientAction = KheperaCommand.AmbientLightCommand(gKheperaWidget)
    #gPositionAction = KheperaCommand.WheelPositionCommand(gKheperaWidget)
        
    # Command interpreter for the K213 messages
    # Output goes either to the K213 widget or (in case of an error or if an
    # unknown command is deteced) to the Console
    #gCameraAction = CameraCommand.CameraCommand(gCameraWidget, gConsoleAction)
    
    # Interpreter that does nothing
    gNullAction=Command.NullCommand(None)

    # Select the command interpreters based on the message prefix

    # A message starting with an "n" contains proximity data
    gDispatcher.addReceiver("n,", gProximityAction)
    # Ambient light string
    #gDispatcher.addReceiver("o,", gAmbientAction)
    # Robot position
    #gDispatcher.addReceiver("h,", gPositionAction)
    # K213 turret
    #gDispatcher.addReceiver("t,2,", gCameraAction)
    # Messages without any further info are thrown away
    vThrowAwayMessages = ["a\r",  # Configure
                        "c\r",  # Set position
                        "d\r",  # Set speed
                        "f\r",  # Configure PID
                        "g\r",  # Set position counter
                        "j\r",  # Configure speed profile
                        "l\r",  # Change led
                        "w\r"]  # Write byte to extension bus
    for vEntry in vThrowAwayMessages:
        gDispatcher.addReceiver(vEntry, gNullAction)

    # If no prefix matches, print message to the Console
    #gDispatcher.addDefaultReceiver(gConsoleAction)


    # Create and start thread to monitor the serialIO
    gMonitorSerIO = monitorSerialIO(writer, gQueue ,sc)
    gMonitorSerIO.start()

    # Attach callback to be invoked as soon as we have some new data in the pipe
    #_tkinter.createfilehandler(reader, READABLE, pipeCallback)

    # Start Tkinter
    #gRoot.mainloop()

if __name__ == '__main__':
    import SerialConnection
    import termios
    sc = SerialConnection.SerialConnection("/dev/ttyS1", termios.B38400)
    sc.writeline("N\n")
    print sc.readline(1)
    #go()
    #gDispatcher.dispatch("n,0,0,0,0,0,0,0,0\r");
    #gDispatcher.dispatch("n\r");
    #gDispatcher.dispatch("n\r");
