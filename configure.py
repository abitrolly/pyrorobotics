#!/usr/bin/env python
# Pyro configure.py script

import sys
from posixpath import exists, isdir, isfile, islink
from posix import popen
import os

def file_exists(file_name, type = 'file'):
    if len(file_name) == 0:
        return 0
    else:
        if exists(file_name):
            if type == 'file' and isfile(file_name):
                return 1
            elif type == 'dir' and isdir(file_name):
                return 1
            else:
                if islink(file_name):
                    print "INFO: using '%s' which is a link" % file_name
                    return 1
                else:
                    return 0
        else:
            return 0

def ask_yn(title, list_of_options):
    print title
    retval = ''
    for directory, desc in list_of_options:
        if ask("Option:    Do you want to build " + desc + "? (y/n)", "n", 0) == "y":
            retval = retval + " " + directory
    return retval

def ask(question, default, filecheck = 1, type = 'file', locate = ''):
   done = 0
   print "-------------------------------------------------------------------"
   while not done:
      print question
      if locate:
          pipe = popen("locate %s | head -1 " % locate )
          default = pipe.readline().strip()
      print 'Default = [' + default + ']: ',
      retval = raw_input()
      if retval == "":
         retval = default
      if retval == 'none':
         done = 1
      elif not filecheck:
         done = 1
      elif file_exists(retval, type):
         done = 1
      else:
         print "WARNING: '%s' does not exist, or wrong type (file or dir)!" % retval
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
                           "/usr/local/include/python" + python_script_name,
                           type = "dir",
                           locate = "include/python" + python_script_name)

python_bin_path = ask("3. What is Python's binary? (enter path and name)",
                           "/usr/local/bin/python" + python_script_name,
                      locate = "bin/python" + python_script_name)

x11_include_dir = ask("4. Where is the X11 include directory?",
                      "/usr/X11",
                      type = "dir",
                      locate = "/usr/X11")

included_packages = ask_yn("\n5. Options:", [
    ('vision/cvision', "Image Processing"),
    ('camera/v4l', "Video for Linux (requires Image Processing)"),
    ('camera/fake', "Simulated vision from files (requires Image Processing)"),
    ('camera/blob', "Stage simulated vision (requires Image Processing)"),
    ('camera/aibo', "Aibo vision (requires Image Processing)"),
    ('camera/robocup', "Robocup simulated vision (requires Image Processing)"),
    ('brain/psom brain/psom/csom_src/som_pak-dev',
     "Self-organizing Map (SOM)"),
    ('tools/cluster', "Cluster Analysis Tool"),
    ('simulators/khepera', "Khepera Simulator"),
    ])

fp = open("Makefile.cfg", "w")
fp.write(text % (python_script_name, python_bin_path, python_include_files,
                 x11_include_dir, included_packages))
fp.close()

print """
Configuration is complete!

You just created Makefile.cfg. You can run this again, or edit
Makefile.cfg by hand if you need to.

Now you are ready to run 'make' (if you aren't already)
"""
