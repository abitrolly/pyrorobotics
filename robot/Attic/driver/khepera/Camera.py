#
#    Class containing the stuff to display the infos from the K213
#   ===============================================================
#
#   Author: Dr. Peter Stoehr        peter@peter-stoehr.de
#   Version:    July 1999 DPS
#               Small changes for the Khepera workshop
#
#               Feb-May 1998 DPS
#               Ported pure Tkinter-version to PMW based one
#
#               May-June 1997 DPS
#               First version
#               
########################################################################

#from Tkinter import *
#import Pmw
#import tkFileDialog
import os
import string
import time
import thread

########################################################################

#from Global import *
#import DisplayWindow

########################################################################

class KheperaCamera:

    # size of the rectangle representing a pixel
    S_SIZE_X = 8
    S_SIZE_Y = 8

    def __init__(self, aRoot, aControl):
        #DisplayWindow.DisplayWindow.__init__(self, aRoot, aControl)

        self.mConfigExits = 0

        self.mLogBuffer = []
        self.mDoLog = Tkinter.IntVar()
        self.mDoLog.set(0)
        self.mLockLog = thread.allocate_lock () 
        self.mFileName="khepera.pgm"
        self.mPath=""
        self.mFileType=[("pgm file", "*.pgm")]


        self.mPixel = {}
        self._compute256grays()

        self.mDoPixel = Tkinter.IntVar()
        self.mDoPixel.set(0)

        self.mDoStat = Tkinter.IntVar()
        self.mDoStat.set(0)

        self.mPicType = Tkinter.IntVar()
        self.mPicType.set(0)

        self.mUpdateFrequenzy = Tkinter.IntVar()
        self.mUpdateFrequenzy.set(1000)

        self._doUpdate = 0

        # Dictionaries to create the buttons of the config widget
        # Structure:
        # 1) Button name
        # 2) Proc to be invoked as soon as the "query" button is pressed
        self.STAT_DATA = {
            "Min value index": self.mRobotControl.getCameraMin,
            "Max value index": self.mRobotControl.getCameraMax,
            "Intensity" : self.mRobotControl.getCameraIntensity }
        # Container to hold the user selected items
        self.mSelectedStat = []

        self.PIC = {
            "Standard resolution" : self.mRobotControl.getCameraPic,
            "Low resolution" : self.mRobotControl.getCameraLowRes,
            "2 times sub" : self.mRobotControl.getCamera2Sub,
            "4 times sub" : self.mRobotControl.getCamera4Sub}

        # Preselected picture update mode
        self.mSelectedPic = "Standard resolution" 

    ####################################################################


    def showWindows(self):
        """ 
        Check if the widget already exists. If not create it and reset
        the variables of the auto update functions.
        """
        if (not self.mWindowsExits or not self.mTopLevel.winfo_exists()):
            self._createWindows()

            # Switch logging and automatic query off
            self.mDoLog.set(0)
            self.mDoPixel.set(0)
            self.mDoStat.set(0)


    ####################################################################

    def displayMin(self, aValue):
        """
        Display the index of the pixel with the darkest pixel.
        aValue holds this index
        This method is called from the CameraCommand instance receiving
        the incoming messages from the robot.
        """
        self.showWindows()
        self.mMin.message("state", str(aValue))
    
    ####################################################################

    def displayMax(self, aValue):
        """
        Display the index of the pixel with the brightest pixel.
        aValue holds this index
        This method is called from the CameraCommand instance receiving
        the incoming messages from the robot.
        """
        self.showWindows()
        self.mMax.message("state", str(aValue))
    
    ####################################################################

    def displayIntensity(self, aMSB, aLSB):
        """
        Display the intensity measured by the camera.
        This method is called from the CameraCommand instance receiving
        the incoming messages from the robot.
        """
        self.showWindows()
        vString = str(aMSB * 256 + aLSB)
        self.mIntensity.message("state", vString)
    
    ####################################################################

    def display(self, aValues):
        """
        Display the picture taken from the K213 vision turret.
        This method is called from different methods of the CameraCommand 
        instance receiving the incoming messages from the robot.
        """
        
        self.showWindows()

        vAction = self.mCanvas.itemconfigure

        # Update the graphic and the strings of the ballon messages
        for i in range(64):
            vAction(self.mPixel[i], fill = self.mGrays[aValues[i]])
            vString = "%dth pixel of the camera : %d" % (i,aValues[i])
            self.mBalloon.tagbind(self.mCanvas, self.mPixel[i], vString,
                    vString)

        # If logging is enabled create a string containing the values
        # and store this string in a global buffer
        if (self.mDoLog.get()):
            vString = ""
            for i in range(64):
                vString = vString + str(aValues[i]) + " "
                if (i % 16 == 1):
                    vString = vString + "\n"

            # Guarded output as writing the log might be done in parallel
            self.mLockLog.acquire()
            self.mLogBuffer.append(vString)
            self.mLockLog.release()


    ####################################################################
        
    def _compute256grays(self):
        """
        Pre-calculate and store the color information needed to display
        the pixels of the K213 turret correctly.
        """
       
        self.mGrays = {}
       
        # Fetch info from the global Pmw-instance 
        vDiv = 256 / gPmwDefaults.getMaxGray()
        for i in range(256):
            self.mGrays[i] = gPmwDefaults.getGray(i / vDiv)
        # The gray value -1 is used if not all pixels have to draw
        # Use "red" fpr this 
        self.mGrays[-1] = "#FF0000"

    ####################################################################


    def _createWindows(self):
        """
        Build the complete widget to display all infos describing a 
        k213 turret.
        """
        # Windo exists
        self.mWindowsExits = 1

        # --------------------------------------------------------------
        
        self.mTopLevel = Toplevel(self.mRoot)
        self.mTopLevel.title("Khepera K213 camera view")
        self.mTopLevel.resizable(0,0)
        
        # --------------------------------------------------------------

        self.mBalloon = Pmw.Balloon(self.mRoot)
        self.mBalloon.configure(state = 'status')

        # --------------------------------------------------------------

        # Create the Menubar
        self.mMenuBar = Pmw.MenuBar(self.mTopLevel, balloon=self.mBalloon)
        self.mMenuBar.pack(expand=1, fill="x", side="top")

        self.mMenuBar.addmenu("File", "File handling")
       	self.mMenuBar.addmenuitem('File', 
                                  'command', 
                                  'Close this window',
	                          command = self._close,
	                          label = 'Close')

        self.mMenuBar.addmenu("Query", 
                              "Query information from the Khepera camera")
       	self.mMenuBar.addmenuitem("Query", 
                                  "command",
                                  "Query information",
                                  command=self.doQuery,
                                  label="Query ...")

        self.mMenuBar.addmenu("Logging", "Log camera data")
       	self.mMenuBar.addmenuitem("Logging", 
                                  "checkbutton",
                                  "Enable or disable logging",
                                  command=self._doLogging,
                                  variable=self.mDoLog,
                                  label = "Do logging")
       	self.mMenuBar.addmenuitem("Logging", 
                                  "separator")
        self.mMenuBar.addmenuitem("Logging",
                                  "command",
                                  "Save camera log as pgm-file",
                                  command=self._saveLog,
                                  label = "Save ...")

        self.mMenuBar.addmenu("Update", 
                              "Automatic query mode for sensors")
       	self.mMenuBar.addmenuitem("Update", 
                                  "checkbutton",
                                  "Enable/disable auto-update of the pixel pic",
                                  variable=self.mDoPixel,
                                  command=self._activateSensorUpdate,
                                  label = "Pixel pic")
       	self.mMenuBar.addmenuitem("Update", 
                                  "checkbutton",
                                  "Enable/disable auto-update of the statistic values",
                                  variable=self.mDoStat,
                                  command=self._activateSensorUpdate,
                                  label = "Statistics")
       	self.mMenuBar.addmenuitem("Update", 
                                  "separator")

	self.mMenuBar.addcascademenu("Update", 
                                     "Update-Frequenzy",
		                     "Setup the delay between two automatic updates", 
                                     traverseSpec = 'z',
                                     label="Update")
	for vTime in (250, 500, 1000, 5000):
            vString = str(vTime) + " ms"
	    self.mMenuBar.addmenuitem('Update-Frequenzy',
                                      'radiobutton', 
                                      'Set update time to ' + vString,
                                      variable= self.mUpdateFrequenzy,
                                      value = vTime,
		                      label = vString,
                                      command=self._doSetupUpdateFreq)

        # Setup the id's for the command of changing the scanning period
        self.mScanId = {}
        self.mScanId[250] = 4
        self.mScanId[500] = 5
        self.mScanId[1000] = 6
        self.mScanId[5000] = 7

        # --------------------------------------------------------------

        # Create the canvas used to display the 64 pixels of the K213 turret
        vWidth = self.S_SIZE_X * 64
        vHeight = self.S_SIZE_Y 
        self.mCanvas = Pmw.ScrolledCanvas(self.mTopLevel, 
                                          canvas_height=vHeight,
                                          canvas_width=vWidth)


        self._drawCamera(self.mCanvas)

        self.mCanvas.pack(expand=1, fill="both", side="top")

        # --------------------------------------------------------------

        # Create an area at the bottom to display the online help
        # and various info items of the turret
        vFrame = Pmw.Group(self.mTopLevel,
                           tagindent = 0,
                           tag_pyclass=None)
        vFrame.pack(expand=1, fill="x", side="top")
        vInterior = vFrame.interior()

        # Contaier for the online help
        self.mMessageBar = Pmw.MessageBar(vInterior,
                                          entry_font = 
                                          gPmwDefaults.getHelpFont())
        self.mMessageBar.pack(expand=1, fill="x", side="left") 

        # Container of the index of the darkest pixel
        self.mMin = Pmw.MessageBar(vInterior,
                                   entry_font = 
                                   gPmwDefaults.getHelpFont(),
                                   label_text=" Min:",
                                   labelpos="w",
                                   entry_width=2)
        self.mMin.message("state", "--")
        self.mMin.pack(fill="x", side="left") 

        # Container of the index of the brightest pixel
        self.mMax = Pmw.MessageBar(vInterior,
                                   entry_font = 
                                   gPmwDefaults.getHelpFont(),
                                   label_text=" Max:",
                                   labelpos="w",
                                   entry_width=2)
        self.mMax.message("state", "--")
        self.mMax.pack(fill="x", side="left") 

        # Container of the intensity meassured by the K213 turret
        self.mIntensity = Pmw.MessageBar(vInterior,
                                       entry_font = 
                                       gPmwDefaults.getHelpFont(),
                                       label_text=" Intensity:",
                                       labelpos="w",
                                       entry_width=4)
        self.mIntensity.message("state", "----")
        self.mIntensity.pack(fill="x", side="left") 

        self.mBalloon.configure(statuscommand = self.mMessageBar.helpmessage)

    ####################################################################

    def _drawCamera(self, aCanvas):
        """
        Create 64 rectangles representing the pixels of the K213 turret
        """
        vWhite = gPmwDefaults.getGray(gPmwDefaults.getMaxGray()-1)
        vBlack = gPmwDefaults.getGray(0)

        vArea = aCanvas.interior()
        
        x1 = 0
        y1 = 0
    
        for i in range(64):
            if (i % 2 == 0):
                vColor = vWhite
            else:
                vColor = vBlack
            self.mPixel[i]= aCanvas.create_rectangle(x1, y1,
                                                     x1+self.S_SIZE_X,
                                                     y1+self.S_SIZE_Y,
                                                     fill=vColor)
            vString = "%dth pixel of the camera" % (i,)
            self.mBalloon.tagbind(aCanvas, self.mPixel[i], vString)
            x1 = x1 + self.S_SIZE_X

    ####################################################################

    def _close(self):
        """
        Callback used to close the camera widget. Triggered by the 
        File/close menu item.
        """
        self.mDoLog.set(0)
        self.mDoPixel.set(0)
        self.mDoStat.set(0)
        self._doUpdate = 0

        self.mTopLevel.destroy()

    ####################################################################

    def _activateSensorUpdate(self):
        """
        Callback used to start the automatic update of the camera info.
        """
        vOldUpdateState = self._doUpdate

        self._doUpdate = (self.mDoPixel.get() or self.mDoStat.get())

        if (self._doUpdate and (not vOldUpdateState)): 
            self._doSensorUpdate()
            
    # ------------------------------------------------------------------

    def _doSensorUpdate(self):
        """
        Callback used to display the information from K213 turret 
        peridocally.
        This task is started and stopped by the user via the "Update" 
        menu. Rescheduling is done by this callback automatically.
        """

        # Check if we still should do an auto update
        if (not self._doUpdate):
            return

        try:
            # Check if the camera pic should be fetched and displayed
            if (self.mDoPixel.get()):
                # Send a request for the data
                self.PIC[self.mSelectedPic]()

            # Check if the statistic info should be fetched and displayed
            if (self.mDoStat.get()):
                self.mRobotControl.getCameraIntensity()
                self.mRobotControl.getCameraMin()
                self.mRobotControl.getCameraMax()

            # Reschedule the task, schedule time is set via the update menu
            self.mRoot.after(self.mUpdateFrequenzy.get(), self._doSensorUpdate) 
        except TimeOut:
            self.showTimeoutMessage()

        self.mRoot.update_idletasks()

    ####################################################################

    def _doSetupUpdateFreq(self):
        """
        After the user changed the update frequency the corresponding
        scanning period has to be set at the K213 vision turret
        """

        vID = self.mScanId[self.mUpdateFrequenzy.get()]
        self.mRobotControl.setCameraScanningPeriod(vID)

    ####################################################################

    def _doLogging(self):
        """
        Callback method triggered from the log menu.
        If we start logging, erase the log buffer.
        """
        if (self.mDoLog.get()):
            self.mLog = []
    
    ####################################################################

    def _saveLog(self):
        """
        Callback method triggered from the log menu to save the stored
        picture as a pgm picture.
        """

        # Create a copy of the log buffer
        self.mLockLog.acquire()
        vBuffer = self.mLogBuffer
        self.mLockLog.release()

        # Ask for the filename
        vSelector = tkFileDialog.SaveAs()
        vFileName = vSelector.show(initialfile=self.mFileName,
                                   initialdir=self.mPath,
                                   filetypes=self.mFileType)
        if (not vFileName):
            return

        # Create the pgm header
        vHeader = "P2\n64 %d\n255\n" % (len(vBuffer))
        vTimeStamp = time.strftime("%x %X", time.localtime(time.time()))
        vLogInfo = "# Log saved at: %s\n" % (vTimeStamp,)

        # Open file
        vFile = open(vFileName,"w")
        # Write header
        vFile.write(vHeader)
        vFile.write(vLogInfo)
        
        # Write the pixelinfo
        vFile.writelines(vBuffer)
        vFile.close()
    
        # Store the user fileinfo for later use
        (self.mPath,self.mFileName) = os.path.split(vFileName)

    ####################################################################

    def doQuery(self):
        """
        Callback triggered by the user via the query menu-item.
        Tasks:
           1) Create the widget
           2) Attach callbacks to the buttons
        """
        # If users has the widget open and presses query again bring
        # widget into the foregroudn
        if (self.mConfigExits and self.mConfigTopLevel.winfo_exists()):
            self.mConfigTopLevel.lift()
            return

        self.mConfigExits = 1

        # Create a container
        self.mConfigTopLevel = Toplevel(self.mRoot)
        self.mConfigTopLevel.title("Query the Khepera camera")

        # Subcontainer used for storing the button bars
        vSelectFrame = Pmw.Group(self.mConfigTopLevel, tag_pyclass=None)
        vSelectFrame.pack(expand=1, fill="both", side="top")
        vSelectArea = vSelectFrame.interior()

        # First button bar used to select the picture mode
        vBox = Pmw.Group(vSelectArea, tag_text="Picture mode")
        vIn = vBox.interior()
        self.mConfigPic = Pmw.RadioSelect(vIn,
                                          buttontype = "radiobutton",
                                          command = self._setCameraMode,
                                          orient = "vertical")

        # Create the buttons using the struct defined in the constructor
        for vStr in self.PIC.keys():
            self.mConfigPic.add(vStr)

        # Preselect the item selected by the user last time
        self.mConfigPic.invoke(self.mSelectedPic)

        self.mConfigPic.pack(expand=1, 
                             fill="x", 
                             side="left",
                             anchor="nw",
                             padx=2,
                             pady=2)
        vBox.pack(expand=1, fill="both", side="left", anchor="nw",
                  padx=4, pady=4)


        # Second button bar used to select the statistic data to be fetched
        vBox = Pmw.Group(vSelectArea, tag_text="Statistic data")
        vIn = vBox.interior()
        self.mConfigStat = Pmw.RadioSelect(vIn,
                                          buttontype = "checkbutton",
                                          orient="vertical")
        # Create the buttons using the struct defined in the constructor
        for vStr in self.STAT_DATA.keys():
            self.mConfigStat.add(vStr)

        # Preselect the items selected by the user last time
        for vStr in self.mSelectedStat:
            self.mConfigStat.invoke(vStr)

        self.mConfigStat.pack(expand=1, 
                             fill="x", 
                             side="right",
                             anchor="nw",
                             padx=2,
                             pady=2)
        vBox.pack(expand=1, fill="both", side="left", anchor="nw",
                  padx=4, pady=4)

        # Create a button-bar to trigger the query command
        vButtonBox = Pmw.ButtonBox(self.mConfigTopLevel)
        vButtonBox.add("Query", 
                       command=self._configQuery)
        vButtonBox.add("Close", 
                       command=self._configExit)
        vButtonBox.pack(expand=1, fill="x", side="top")
         

    # ------------------------------------------------------------------

    def _configQuery(self):
        """
        Callback triggered by the query-button of the Query-widget.
        """
        
        # Handle timeout messages from the serial IO
        try:
            # Get the item selected by the user definig the statistics
            self.mSelectedStat = self.mConfigStat.getcurselection()
            # Call the appropriated methods using the struct created 
            # in __init__
            for vSelected in self.mSelectedStat:
                self.STAT_DATA[vSelected]()

            # Send a request for the data
            self.PIC[self.mSelectedPic]()
        except TimeOut:
            self.showTimeoutMessage()

    # ------------------------------------------------------------------
    
    def _setCameraMode(self, tag):
        self.mSelectedPic = tag
    
    # ------------------------------------------------------------------

    def _configExit(self):
        """
        Callback triggered by the exit-button of the query-widget.
        """
        self.mConfigTopLevel.destroy()

