from os import environ
from pyro.system import file_exists
import ConfigParser
import string

class Configuration:
    def __init__(self, file = None):
        self.data = {
            "robot":       {},
            "brain":       {},
            "simulator":   {},
            "pioneer":     {},
            "khepera":     {},
            "aria":        {},
            "srisim":      {},
            "pyro":        {}
            }
        if file != None:
            self.load(file)

    def display(self):
        for sec in self.data.keys():
            print "[%s]" % sec
            for opt in self.data[sec].keys():
                print opt, "=", self.data[sec][opt]
            print

    def get(self, name, opt):
        try:
            return self.data[name][opt]
        except:
            return None

    def put(self, name, opt, value):
        if not self.data.has_key(name):
            self.data[name] = {}
        self.data[name][opt] = value

    def processFile(self, file, cp):
        cp.read(file)
        for sec in cp.sections():
            name = string.lower(sec)
            if not self.data.has_key(name):
                self.data[name] = {}
            for opt in cp.options(sec):
                self.data[name][string.lower(opt)] = string.strip(cp.get(sec, opt))

    def load(self, file = None):
        cp = ConfigParser.ConfigParser()
        if file_exists( environ['PYRO'] + "/.pyro"): # $PYRO?
            self.processFile( environ['PYRO'] + "/.pyro", cp)
        if file_exists( environ['PYRO'] + "/pyro.ini"): # $PYRO?
            self.processFile( environ['PYRO'] + "/pyro.ini", cp)
        if file_exists( environ['PYRO'] +
                        "/.pyro-" + environ['HOSTNAME']):
            # $PYRO-HOSTNAME?
            self.processFile( environ['PYRO'] +
                              "/.pyro-" + environ['HOSTNAME'], cp)
        if file_exists( environ['PYRO'] +
                        "/pyro-" + environ['HOSTNAME'] + ".ini"):
            # $PYRO-HOSTNAME?
            self.processFile( environ['PYRO'] +
                              "/pyro-" + environ['HOSTNAME'] + ".ini", cp)
        if file_exists( environ['HOME'] + "/.pyro"): # home dir?
            self.processFile( environ['HOME'] + "/.pyro", cp)
        if file_exists( environ['HOME'] + "/pyro.ini"): # home dir?
            self.processFile( environ['HOME'] + "/pyro.ini", cp)
        if file_exists(".pyro"): # current dir?
            self.processFile( ".pyro", cp)
        if file_exists("pyro.ini"): # current dir?
            self.processFile( "pyro.ini", cp)
        if file and file_exists(file):
            self.processFile( file, cp)

if __name__ == "__main__":
    config = Configuration()
    config.load("some.ini")
    config.display()
