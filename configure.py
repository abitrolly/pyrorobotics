# Pyro configure.py script

import sys

def ask(question, default):
   print "-----------------------"
   print question
   print '[' + default + ']: ',
   retval = raw_input()
   if retval == '' or retval == 'none':
      return default
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

# Where is this version of Python's include files?
PYTHON_INCLUDE=-I%s

# Where is Saphira? Leave empty if you don't want to build
# Saphira-related items.
SAPHIRA=%s

# Where are X11 files (such as X11 include directory)?
X11_DIR = %s
"""

print """
What version of Python do you want to build Pyro for?
(Leave empty if your Python binary is just "python")
If you need to type 'python2.2' to run Python, then
enter "2.2".
"""
python_script_name = ask("1. Python version number?", "")

python_include_files = ask("2. Where are Python's include files?",
                           "/usr/local/include/python2.2")

saphira =ask("3. Where is Saphira? (Type 'none' if you don't have it)",
             "/usr/local/saphira/ver62")

x11_include_dir = ask("4. Where is the X11 include directory?",
                      "/usr/X11")

fp = open("Makefile.cfg", "w")
fp.write(text % (python_script_name, python_include_files,
                 saphira, x11_include_dir))
fp.close()

print """
Configuration is complete!

You just created Makefile.cfg. You can run this again, or edit
Makefile.cfg by hand if you need to.

Now you are ready to run 'make'
"""
