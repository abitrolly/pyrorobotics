import string
import sys 

def usage():
    print "Pyro - Robotics in Python"
    print "-------------------------"
    print "  -h this help"
    print "  -r load a robot file"
    print "  -b load a brain file"
    print ""

def help():
    print "--------------------------------------------------"
    print "Pyro commands:"
    print "--------------------------------------------------"
    print "! <command>            execute <command> in Python"
    print "% <command>            execute <command> in shell"
    print "brain                  load a brain file"
    print "edit                   edit the brain file"
    print "help                   this help message"
    print "quit | exit | bye      exit from Pyro"
    print "reload                 reload the brain"
    print "robot                  load a robot file"
    print "run                    start brain running"
    print "stop                   stop brain and robot"
    print "--------------------------------------------------"

def file_exists(file_name):
    from posixpath import exists
    if len(file_name) == 0:
        return 0
    else:
        return exists(file_name)
    
def loadINIT(filename, robot=0, redo=0):
    path = filename.split("/")
    modulefile = path.pop() # module name
    module = modulefile.split(".")[0]
    search = string.join(path, "/")
    oldpath = sys.path[:] # copy

    sys.path.append(search)

    exec("import " + module + " as userspace")

    if redo:
        reload(userspace)

    sys.path = oldpath
    if robot is 0:
	return userspace.INIT()
    else:
	return userspace.INIT(robot)
