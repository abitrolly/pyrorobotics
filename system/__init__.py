import string
import sys 

def usage():
    print "Pyro - Robotics in Python"
    print "-------------------------"
    print "  -h this help"
    print "  -r load a robot file"
    print "  -b load a brain file"
    print "  -o pass arguments to a brain (separated by ':')"
    print "  -s load a simulator"
    print ""

def help():
    print "--------------------------------------------------"
    print "Pyro commands:"
    print "--------------------------------------------------"
    print "<command>              execute <command> in Python"
    print "<exp>                  print <exp> in Python"
    print "% <command>            execute <command> in shell"
    print "edit                   edit the brain file"
    print "help                   this help message"
    print "load brain             load a brain file"
    print "load robot             load a robot file"
    print "quit | exit | bye      exit from Pyro"
    print "reload                 reload the brain"
    print "run                    start brain running"
    print "stop                   stop brain and robot"
    print "--------------------------------------------------"
    print "  GUI Command line editing:"
    print "--------------------------------------------------"
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
