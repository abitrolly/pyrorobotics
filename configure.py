# Pyro configure.py script

import sys
from posixpath import exists

def file_exists(file_name):
    if len(file_name) == 0:
        return 0
    else:
        return exists(file_name)

def ask_yn(title, list_of_options):
    print title
    retval = ''
    for directory, desc in list_of_options:
        if ask("Option:    Do you want to build " + desc + "? (y/n)", "n", 0) == "y":
            retval += " " + directory
    return retval

def ask(question, default, filecheck = 1):
   done = 0
   print "-------------------------------------------------------------------"
   while not done:
      print question
      print '[' + default + ']: ',
      retval = raw_input()
      if retval == "":
         retval = default
      if retval == 'none':
         done = 1
      elif not filecheck:
         done = 1
      elif file_exists(retval):
         done = 1
      else:
         print "WARNING: doesn't exist: '%s'" % retval
   if retval == 'none':
      return ''
   else:
      return retval

print """
---------------------------------------------------------------------
This is the configure.py script for installing Pyro, Python Robotics.
Pressing ENTER by itself will accept the default (shown in brackets).
---------------------------------------------------------------------
"""
text = """
# Pyro - Python Robotics Config Script

# What version of Python do you want to build Pyro for?
# Leave empty if your python binary is just "python"
PYTHON_VERSION=%s

# Where exactly is python?
PYTHON_BIN=%s

# Where is this version of Python's include files?
PYTHON_INCLUDE=-I%s

# Where is Saphira? Leave empty if you don't want to build
# Saphira-related items.
SAPHIRA=%s

# Where are X11 files (such as X11 include directory)?
X11_DIR = %s

# What subdirs to include in the make process?
CONFIGDIRS = %s

"""

print """
What version of Python do you want to build Pyro for?
(Leave empty if your Python binary is just "python")
If you need to type 'python2.2' to run Python, then
enter "2.2".
"""
python_script_name = ask("1. Python version number?", "", 0)

python_include_files = ask("2. Where are Python's include files?",
                           "/usr/local/include/python" + python_script_name)

python_bin_path = ask("3. Where is Python's binary? (enter path and name)",
                           "/usr/local/bin/python" + python_script_name)

saphira =ask("4. Where is Saphira? (Type 'none' if you don't have it)",
             "/usr/local/saphira/ver62")

x11_include_dir = ask("5. Where is the X11 include directory?",
                      "/usr/X11")

included_packages = ask_yn("\n6. Options:", [
    #('camera/bt848',"BT848 camera"),
    #('geometry', "Test Geometry C code"),
    #('gui/3DArray', "Test 3D Array Code"),
    #('robot/driver/grid', "Test C Grid"),
    #('robot/driver/video', "Test Video"),
    ('camera/v4l', "Video for Linux (v4l)"),
    ('brain/psom brain/psom/csom_src/som_pak-dev',
     "Self-organizing Map (SOM)"),
    ('tools/cluster', "Cluster Analysis Tool"),
    ('simulators/khepera', "Khepera Simulator"),
    ])

#camera/bt848 geometry gui/3DArray robot/driver/grid \
#	robot/driver/video camera/v4l brain/psom tools/cluster \
#	brain/psom/csom_src/som_pak-dev simulators/khepera

fp = open("Makefile.cfg", "w")
fp.write(text % (python_script_name, python_bin_path, python_include_files,
                 saphira, x11_include_dir, included_packages))
fp.close()

print """
Configuration is complete!

You just created Makefile.cfg. You can run this again, or edit
Makefile.cfg by hand if you need to.

Now you are ready to run 'make'
"""
