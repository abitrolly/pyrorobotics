from Tkinter import *

class StatusBar(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)
      self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
      self.label.pack(fill=X)

   def set(self, format, *args):
      self.label.config(text=format % args)
      self.label.update_idletasks()

   def clear(self):
      self.label.config(text="")
      self.label.update_idletasks()


####
#	Class Dialog
#
#	Purpose
#	Base class for many dialog box classes.
####

class Dialog:

	def __init__(self, master):
		self.master = master
		self.top = Toplevel(self.master)
		self.top.title(self.__class__.__name__)
		self.top.minsize(1, 1)
		self.myWaitVar = `self.top` + 'EndDialogVar'

	def Show(self):
		self.SetupDialog()
		self.CenterDialog()
		self.top.deiconify()
		self.top.focus()

	def TerminateDialog(self, withValue):
		self.top.setvar(self.myWaitVar, withValue)
		self.top.withdraw()
		
	def DialogCleanup(self):
		self.top.destroy()
		self.master.focus()

	def SetupDialog(self): 
		pass

	def CenterDialog(self):
		self.top.withdraw()
		self.top.update_idletasks()
		w = self.top.winfo_screenwidth()
		h = self.top.winfo_screenheight()
		reqw = self.top.winfo_reqwidth()
		reqh = self.top.winfo_reqheight()
		centerx = `(w-reqw)/2`
		centery = `(h-reqh)/2 - 100`
		geomStr = "+" + centerx + "+" + centery
		self.top.geometry(geomStr)

####
#	Class ModalDialog
#
#	Purpose
#	Base class for many modal dialog box classes.
####

class ModalDialog(Dialog):

	def __init__(self, master):
		Dialog__init__(self, master)

	def Show(self):
		import string
		self.SetupDialog()
		self.CenterDialog()
		self.top.grab_set()
		self.top.focus()
		self.top.deiconify()
		self.top.waitvar(self.myWaitVar)
		return string.atoi(self.top.getvar(self.myWaitVar))
####
#	Class AlertDialog
#
#	Purpose
#	-------
#
#	AlertDialog's are widgets that allow one to pop up warnings, one line
#	questions etc. They return a set of standard action numbers being :-
#	0 => Cancel was pressed
#	1 => Yes was pressed
#	2 => No was pressed
#
#	Standard Usage
#	--------------
#
#	F = AlertDialog(widget, message)
#	action = F.Show()
####

class AlertDialog(ModalDialog):

	def __init__(self, widget, msg):
		self.widget = widget
		self.msgString = msg
		Dialog.__init__(self, widget)

	def SetupDialog(self):
		import string
		upperFrame = Frame(self.top)
		upperFrame['relief'] = 'raised'
		upperFrame['bd']	 = 1
		upperFrame.pack({'expand':'yes', 'side':'top', 'fill':'both' })
		self.bitmap = Label(upperFrame)
		self.bitmap.pack({'side':'left'})
		msgList = string.splitfields(self.msgString, "\n")
		for i in range(len(msgList)):
			msgText = Label(upperFrame)
			msgText["text"]	  = msgList[i]
			msgText.pack({'expand':'yes', 'side':'top', 'anchor':'nw', 
				'fill':'x' })
		self.lowerFrame = Frame(self.top)
		self.lowerFrame['relief'] = 'raised'
		self.lowerFrame['bd']	 = 1
		self.lowerFrame.pack({'expand':'yes', 'side':'top', 'pady':'2', 
			'fill':'both' })

	def OkPressed(self):
		self.TerminateDialog(1)

	def CancelPressed(self):
		self.TerminateDialog(0)

	def NoPressed(self):
		self.TerminateDialog(2)

	def CreateButton(self, text, command):
		self.button = Button(self.lowerFrame)
		self.button["text"]	  = text
		self.button["command"]   = command
		self.button.pack({'expand':'yes', 'pady':'2', 'side':'left'})

####
#	Class ErrorDialog
#
#	Purpose
#	-------
#
#	To pop up an error message
####

class ErrorDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'error'
		self.CreateButton("OK", self.OkPressed)

####
#	Class WarningDialog
#
#	Purpose
#	-------
#
#	To pop up a warning message.
####

class WarningDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'warning'
		self.CreateButton("Yes", self.OkPressed)
		self.CreateButton("No", self.CancelPressed)

####
#	Class QuestionDialog
#
#	Purpose
#	-------
#
#	To pop up a simple question
####

class QuestionDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'question'
		self.CreateButton("Yes", self.OkPressed)
		self.CreateButton("No", self.NoPressed)
		self.CreateButton("Cancel", self.CancelPressed)

####
#	Class MessageDialog
#
#	Purpose
#	-------
#
#	To pop up a message.
####

class MessageDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'warning'
		self.CreateButton("Dismiss", self.CancelPressed)

####
#	Class FileDialog
#
#	Purpose
#	-------
#
#	FileDialog's are widgets that allow one to select file names by
#	clicking on file names, directory names, filters, etc.
#
#	Standard Usage
#	--------------
#
#	F = FileDialog(widget, some_title, some_filter)
#	if F.Show() != 1:
#		F.DialogCleanup()
#	return
#		file_name = F.GetFileName()
#		F.DialogCleanup()
####

class FileDialog(ModalDialog):

	#	constructor

	def __init__(self, widget, title, filter="*"):
		from os import getcwd
		from string import strip

		self.widget = widget
		self.filter = strip(filter)
		self.orig_dir = getcwd()
		self.cwd = getcwd()
                #	the logical current working directory
		Dialog.__init__(self, widget)

	#	setup routine called back from Dialog

	def SetupDialog(self):

		# directory label

		self.dirFrame = Frame(self.top)
		self.dirFrame['relief'] = 'raised'
		self.dirFrame['bd']	 = '2'
		self.dirFrame.pack({'expand':'no', 'side':'top', 'fill':'both'})
		self.dirLabel = Label(self.dirFrame)
		self.dirLabel["text"] = "Directory:"
		self.dirLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})

		# editable filter

		self.filterFrame = Frame(self.top)
		self.filterFrame['relief'] = 'raised'
		self.filterFrame['bd']	 = '2'
		self.filterFrame.pack({'expand':'no', 'side':'top', 'fill':'both'})
		self.filterLabel = Label(self.filterFrame)
		self.filterLabel["text"] = "Filter:"
		self.filterLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
		self.filterEntry = Entry(self.filterFrame)
		self.filterEntry.bind('<Return>', self.FilterReturnKey)
		self.filterEntry["width"]  = "40"
		self.filterEntry["relief"] = "ridge"
		self.filterEntry.pack({'expand':'yes', 'side':'right', 'fill':'x'})
		self.filterEntry.insert(0, self.filter)

		# the directory and file listboxes

		self.listBoxFrame = Frame(self.top)
		self.listBoxFrame['relief'] = 'raised'
		self.listBoxFrame['bd']	 = '2'
		self.listBoxFrame.pack({'expand':'yes', 'side' :'top',
			'pady' :'2', 'padx': '0', 'fill' :'both'})
		self.CreateDirListBox()
		self.CreateFileListBox()
		self.UpdateListBoxes()

		# editable filename

		self.fileNameFrame = Frame(self.top)
		self.fileNameFrame.pack({'expand':'no', 'side':'top', 'fill':'both'})
		self.fileNameFrame['relief'] = 'raised'
		self.fileNameFrame['bd']	 = '2'
		self.fileNameLabel = Label(self.fileNameFrame)
		self.fileNameLabel["text"] = "File:"
		self.fileNameLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
		self.fileNameEntry = Entry(self.fileNameFrame)
		self.fileNameEntry["width"]  = "40"
		self.fileNameEntry["relief"] = "ridge"
		self.fileNameEntry.pack({'expand':'yes', 'side':'right', 'fill':'x'})
		self.fileNameEntry.bind('<Return>', self.FileNameReturnKey)

		#	buttons - ok, filter, cancel

		self.buttonFrame = Frame(self.top)
		self.buttonFrame['relief'] = 'raised'
		self.buttonFrame['bd']	 = '2'
		self.buttonFrame.pack({'expand':'no', 'side':'top', 'fill':'x'})
		self.okButton = Button(self.buttonFrame)
		self.okButton["text"]	  = "OK"
		self.okButton["command"]   = self.OkPressed
		self.okButton["width"] = 8
		self.okButton.pack({'expand':'yes', 'pady':'2', 'side':'left'})
		self.filterButton = Button(self.buttonFrame)
		self.filterButton["text"]	  = "Filter"
		self.filterButton["command"]   = self.FilterPressed
		self.filterButton["width"] = 8
		self.filterButton.pack({'expand':'yes', 'pady':'2', 'side':'left'})
		button = Button(self.buttonFrame)
		button["text"] = "Cancel"
		button["command"] = self.CancelPressed
		button["width"] = 8
		button.pack({'expand':'yes', 'pady':'2', 'side':'left'})

	#	create the directory list box

	def CreateDirListBox(self):
		frame = Frame(self.listBoxFrame)
		frame.pack({'expand':'yes', 'side' :'left', 'pady' :'1', 
			'fill' :'both'})
		frame['relief'] = 'raised'
		frame['bd']	 = '2'
		filesFrame = Frame(frame)
		filesFrame['relief'] = 'flat'
		filesFrame['bd']	 = '2'
		filesFrame.pack({'side':'top', 'expand':'no', 'fill':'x'})
		label = Label(filesFrame)
		label['text'] = 'Directories:'
		label.pack({'side':'left', 'expand':'yes', 'anchor':'w',
			'fill':'none'})
		scrollBar = Scrollbar(frame, {'orient':'vertical'})
		scrollBar.pack({'expand':'no', 'side':'right', 'fill':'y'})
		self.dirLb = Listbox(frame, {'yscroll':scrollBar.set})
		self.dirLb.pack({'expand':'yes', 'side' :'top', 'pady' :'1', 
			'fill' :'both'})
		self.dirLb.bind('<Double-Button-1>', self.DoDoubleClickDir)
		scrollBar['command'] = self.dirLb.yview

	#	create the files list box

	def CreateFileListBox(self):
		frame = Frame(self.listBoxFrame)
		frame['relief'] = 'raised'
		frame['bd']	 = '2'
		frame.pack({'expand':'yes', 'side' :'left', 'pady' :'1', 'padx' :'1', 
			'fill' :'both'})
		filesFrame = Frame(frame)
		filesFrame['relief'] = 'flat'
		filesFrame['bd']	 = '2'
		filesFrame.pack({'side':'top', 'expand':'no', 'fill':'x'})
		label = Label(filesFrame)
		label['text'] = 'Files:'
		label.pack({'side':'left', 'expand':'yes', 'anchor':'w', 
			'fill':'none'})
		scrollBar = Scrollbar(frame, {'orient':'vertical'})
		scrollBar.pack({'side':'right', 'fill':'y'})
		self.fileLb = Listbox(frame, {'yscroll':scrollBar.set})
		self.fileLb.pack({'expand':'yes', 'side' :'top', 'pady' :'0', 
			'fill' :'both'})
		self.fileLb.bind('<1>', self.DoSelection)
		self.fileLb.bind('<Double-Button-1>', self.DoDoubleClickFile)
		scrollBar['command'] = self.fileLb.yview

	#	update the listboxes and directory label after a change of directory

	def UpdateListBoxes(self):
		import os
		from commands import getoutput
		from string import splitfields

		cwd = self.cwd
		self.fileLb.delete(0, self.fileLb.size())
		filter = self.filterEntry.get()
		# '*' will list recurively, we don't want that.
		if filter == '*':
			filter = ''
		cmd = "/bin/ls " + os.path.join(cwd, filter) + \
                      " | /bin/grep -v __init__.py"
		cmdOutput = getoutput(cmd)
		files = splitfields(cmdOutput, "\n")
                files.sort()
		for i in range(len(files)):
			if os.path.isfile(os.path.join(cwd, files[i])):
				self.fileLb.insert('end', os.path.basename(files[i]))
		files = os.listdir(cwd)
                if cwd != '/':
                   files.append('..')
		files.sort()
		self.dirLb.delete(0, self.dirLb.size())
		for i in range(len(files)):
                   if os.path.isdir(os.path.join(cwd, files[i])):
                      if files[i] != 'CVS':
                         self.dirLb.insert('end', files[i])
		self.dirLabel['text'] = "Directory:" + self.cwd_print()

	#	selection handlers

	def DoSelection(self, event):
		from posixpath import join
		lb = event.widget
		field = self.fileNameEntry
		field.delete(0, AtEnd())
		field.insert(0, join(self.cwd_print(), lb.get(lb.nearest(event.y))))
                lb.select_clear(0, "end")
                lb.select_anchor(lb.nearest(event.y))


	def DoDoubleClickDir(self, event):
		from posixpath import join
		lb = event.widget
		self.cwd = join(self.cwd, lb.get(lb.nearest(event.y)))
		self.UpdateListBoxes()

	def DoDoubleClickFile(self, event):
		self.OkPressed()

	def OkPressed(self):
		self.TerminateDialog(1)

	def FileNameReturnKey(self, event):
		from posixpath import isabs, expanduser, join
		from string import strip
		#	if its a relative path then include the cwd in the name
		name = strip(self.fileNameEntry.get())
		if not isabs(expanduser(name)):
			self.fileNameEntry.delete(0, 'end')
			self.fileNameEntry.insert(0, join(self.cwd_print(), name))
		self.okButton.flash()
		self.OkPressed()
	
	def FilterReturnKey(self, event):
		from string import strip
		filter = strip(self.filterEntry.get())
		self.filterEntry.delete(0, 'end')
		self.filterEntry.insert(0, filter)
		self.filterButton.flash()
		self.UpdateListBoxes()

	def FilterPressed(self):
		self.UpdateListBoxes()

	def CancelPressed(self):
		self.TerminateDialog(0)

	def GetFileName(self):
		return self.fileNameEntry.get()
		
	#	return the logical current working directory in a printable form
	#	ie. without all the X/.. pairs. The easiest way to do this is to
	#	chdir to cwd and get the path there.

	def cwd_print(self):
		from os import chdir, getcwd
		chdir(self.cwd)
		p = getcwd()
		chdir(self.orig_dir)
		return p

####
#	Class LoadFileDialog
#
#	Purpose
#	-------
#
#	Specialisation of FileDialog for loading files.
####

class LoadFileDialog(FileDialog):

	def __init__(self, master, title, filter):
		FileDialog.__init__(self, master, title, filter)
		self.top.title(title)

	def OkPressed(self):
		fileName = self.GetFileName()
		if file_exists(fileName) == 0:
			str = 'File ' + fileName + ' not found.'
			errorDlg = ErrorDialog(self.top, str)
			errorDlg.Show()
			errorDlg.DialogCleanup()
			return
		FileDialog.OkPressed(self)

####
#	Class SaveFileDialog
#
#	Purpose
#	-------
#
#	Specialisation of FileDialog for saving files.
####

class SaveFileDialog(FileDialog):

	def __init__(self, master, title, filter):
		FileDialog.__init__(self, master, title, filter)
		self.top.title(title)

	def OkPressed(self):
		fileName = self.GetFileName()
		if file_exists(fileName) == 1:
			str = 'File ' + fileName + ' exists.\nDo you wish to overwrite it?'
			warningDlg = WarningDialog(self.top, str)
			if warningDlg.Show() == 0:
				warningDlg.DialogCleanup()
				return
			warningDlg.DialogCleanup()
		FileDialog.OkPressed(self)

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)


        self.button = Button(self)
        self.button['text'] = 'Load File...'
        self.button['command'] = self.Press
        self.button.pack({"side": "top"})

        self.pack()

    def Press(self):
        fileDlg = filedlg.LoadFileDialog(app, "Load File", "*")
        if fileDlg.Show() != 1:
            fileDlg.DialogCleanup()
            return
        fname = fileDlg.GetFileName()
        self.button['text'] = 'File: ' + fname
        fileDlg.DialogCleanup()
    

#
#	Return whether a file exists or not.
#	The file "" is deemed to not exist
#

def file_exists(file_name):
	from posixpath import exists
	import string
	if len(file_name) == 0:
		return 0
	else:
		return exists(file_name)

#
#	read the lines from a file and strip them of their trailing newlines
#

def readlines(fd):
	from string import strip
	return map(lambda s, f=strip: f(s), fd.readlines())

#
#	Various set operations on sequence arguments.
#	in joins the values in 'a' take precedence over those in 'b'
#

def seq_join(a, b):
	res = a[:]
	for x in b:
		if x not in res:
			res.append(x)
	return res

def seq_meet(a, b):
	res = []
	for x in a:
		if x in b:
			res.append(x)
	return res

def seq_diff(a, b):
	res = []
	for x in a:
		if x not in b:
			res.append(x)
	return res

#
#	Various set operations on map arguments.
#	The values in 'a' take precedence over those in 'b' in all cases.
#

def map_join(a, b):
	res = {}
	for x in a.keys():
		res[x] = a[x]
	for x in b.keys():
		if not res.has_key(x):
			res[x] = b[x]
	return res

def map_meet(a, b):
	res = {}
	for x in a.keys():
		if b.has_key(x):
			res[x] = a[x]
	return res

def map_diff(a, b):
	res = {}
	for x in a.keys():
		if not b.has_key(x):
			res[x] = a[x]
	return res

#
#	Join a map of defaults values with a map of set values. The defaults 
#	map is taken to be total, and hence any keys not in the defaults, but 
#	in the settings, must be errors.
#

def map_join_total(settings, defaults):
	res = map_join(settings, defaults)
	for x in settings.keys():
		if not defaults.has_key(x):
			raise "merge_defaults"
	return res

#
#	Return a string being the concatenation of a sequence of objects
#	NOTE: we apply the routine recursively to sequences of sequences
#

def seq_to_str(s):
	if type(s) == type((1,)) or type(s) == type([]):
		return reduce(lambda sum, a: sum + seq_to_str(a), s, "")
	else:
		return str(s)

#
#	a dummy function for any number of arguments
#

def dummy(*args):
	pass

#
#	the true and false functions for any number of args
#

def true(*args):
	return 1

def false(*args):
	return 0

#
#	return whether a char is printable or not
#

def is_printable(c):
	o = ord(c)
	return c == "\n" or (o >= 32 and o <= 126)

#
#	return a printable version of a given string
#	by simply omitting non printable characters
#

def string_printable(s):
	length = len(s)
	ok = 1
	res = ""
	l = 0
	for i in range(length):
		if not is_printable(s[i]):
			res = res + s[l:i]
			l = i+1
			ok = 0
	if ok:
		return s
	else:
		return res + s[l:length]
