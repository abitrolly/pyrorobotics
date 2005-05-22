#!/usr/bin/env python

from pyrobot.system import file_exists
from pyrobot.tools import OptionHandler, Option
import os, operator, sys, string, inspect, types

# Handle options -------------------------------------------------
opts = OptionHandler("wikidoc")
opts.options = [ #Option("trials",       "t",  1 , int, "0", "Number of trials"),
    ]
args = opts.initialize(sys.argv[1:])
# End Handle options ---------------------------------------------
include__ = 0
showSource = 1 # 0 - no, 1 - first line, 2 - all
includeOthers = 0
# Process data  ---------------------------------------------
for module in args:
    print "= Module %s =\n" % module
    print "This is a reference page for the module {{{%s}}}. You can find the entire reference manual" % module
    print """at ["PyrobotReferenceManual"], and more on the whole project at ["Pyrobot"].\n""" 
    exec("import %s" % module)
    exec("items = dir(%s)" % module)
    for i in items:
        exec("dirList = dir(%s.%s)" % (module, i))
        if "__module__" in dirList:
            exec("moduleName = %s.%s.__module__" % (module, i))
        else:
            moduleName = ""
        if not include__ and not (i[:2] != "__" and i[:-2] != "__" and i != "__init__"): continue
        if not includeOthers and moduleName == '': continue
        print "== Class %s ==\n" % i
        exec("docString = %s.%s.__doc__" % (module, i))
        if "__dict__" in dirList:
            exec("dict = %s.%s.__dict__" % (module, i))
        else:
            dict = {}
        if docString:
            print "{{{"
            print docString
            print "}}}\n"
        if moduleName != module:
            if moduleName:
                print """This class is defined in ["%s"]\n""" % moduleName
                continue
            else:
                print "This class is defined elsewhere.\n"
        for m in dirList:
            exec("obj = %s.%s.%s" % (module, i, m))
            mType = type(obj)
            if mType == types.MethodType and moduleName == module:
                filename = module.replace(".", "/")
                #print filename
                if obj.im_func.func_code.co_filename.find(filename) < 0:
                    #print "This method is defined in ", obj.im_func.func_code.co_filename
                    continue
                if include__ or (m[:2] != "__" and m[:-2] != "__" and m != "__init__"):
                    print "=== Method %s.%s ===\n" % (i, m)
                    if obj.__doc__:
                        print "{{{"
                        print obj.__doc__
                        print "}}}\n"
                    if showSource:
                        if showSource == 2:
                            print "Source code:\n{{{"
                            print inspect.getsource( obj )
                        elif showSource == 1:
                            print "Method parameters:\n{{{"
                            print inspect.getsource( obj ).split("\n")[0]
                        print "}}}\n"
#        if dict != {}:
#            print "--------------------------"
#            for m in dict:
#                print "    ", m

print "--------"
print """End of auto-generated documentation. See ["PyrobotReferenceManual"] for more. (c) 2004 D.S. Blank"""
