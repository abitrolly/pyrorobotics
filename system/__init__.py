import string
import sys
from pyro.system.version import version

def about():
    print "-------------------------------------------------------------"
    print "Pyro - Python Robotics"
    print "Version:", version()
    print "See: http://wiki.cs.brynmawr.edu/?Pyro"
    print "(c) 2003, D.S. Blank"
    print "-------------------------------------------------------------"

def usage():
    about()
    print "  -h                 show this help"
    print "  -r ROBOT           name of robot.py file to load"
    print "  -b BRAIN           name of brain.py file to load"
    print "  -o BRAIN_ARGUMENTS (separated by ':', no spaces)"
    print "  -s SIMULATOR       name of simulator to run"
    print "  -i CONFIGFILE      name of config file to load"
    print "  -c CAMERA          name of camera.py file to load"
    print "  -w WORLDFILE       name of simulator world to load"
    print "  -e \"string\"        eval string of commands"
    print "                     that are ; separated"    
    print ""

def help():
    about()
    print "-------------------------------------------------------------"
    print "Pyro commands:"
    print "-------------------------------------------------------------"
    print "  <command>                   execute <command> in Python"
    print "  <exp>                       print <exp> in Python"
    print "  % <command>                 execute <command> in shell"
    print "  edit                        edit the brain file"
    print "  help                        this help message"
    print "  info                        show brain and robot info"
    print "  load brain                  load a brain file"
    print "  load robot                  load a robot file"
    print "  load simulator              load a simulator"
    print "  quit | exit | bye           exit from Pyro"
    print "  reload                      reload the brain"
    print "  run                         start brain running"
    print "  stop                        stop brain and robot"
    print "-------------------------------------------------------------"
    print "GUI Window Command line editing commands:"
    print "-------------------------------------------------------------"
    print "  Control+p or UpArrow        previous line"
    print "  Control+n or DownArrow      next line"
    print "  Control+a or Home           beginning of line"
    print "  Control+e or End            end of line"
    print "  Control+f or RightArrow     forward one character"
    print "  Control+b or LeftArrow      back one character"
    print ""

def file_exists(file_name):
    from posixpath import exists
    if len(file_name) == 0:
        return 0
    else:
        return exists(file_name)
    
def loadINIT(filename, robot=0, redo=0, brain=0, args=None):
    print "Loading INIT '%s'..." % filename
    path = filename.split("/")
    modulefile = path.pop() # module name
    module = modulefile.split(".")[0]
    search = string.join(path, "/")
    oldpath = sys.path[:] # copy

    sys.path.append(search)
    
    exec("import " + module + " as userspace")
    print 'Loaded ' + module

    if redo:
        reload(userspace)

    sys.path = oldpath
    if brain is 0:
        if robot is 0:
            return userspace.INIT()
        else:
            if args:
                return userspace.INIT(robot, args)
            else:
                return userspace.INIT(robot)
    else:
        return userspace.INIT(robot, brain)

