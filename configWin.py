import compileall, os

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

os.system('copy build\pyrobot bin\pyrobot.pyw')

compileall.compile_dir(".")
