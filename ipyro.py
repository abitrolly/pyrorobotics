#
# IPyron (= Pyro + IPython) python module
# by Pierre-Antoine Champin (pierre-antoine.champin at iuta.univ-lyon1.fr)
#

from IPython.Shell import IPShellEmbed 
_banner ="""
Welcome to IPyro

by Pierre-Antoine Champin (pierre-antoine.champin at iuta.univ-lyon1.fr)
(c)2004 University Claude Bernard Lyon 1

Useful names:
  gui:    the pyro GUI object
  engine: the pyro engine
  robot:  the loaded robot, if any
  h:      the pyro hierarchy, accessible as a python object (type 'h?' for info)
"""

_bye = """
See you later...
(you will be sent back to Pyro command line,
 type 'ipyro_shell()' to come back to IPyro)
"""

ipyro_shell = IPShellEmbed([], _banner, _bye) 

class PyroHierarchy (object):
    """
    A wrapper class for the pyro devices hierarchy.
    An instance of this class represents a node of the hierarchy,
    with an attribute for every subnode.
    Getting an attribute is equivalent to using robot.get .
    Setting an attribute is equivalent to using robot.set .
    Numeric nodes can be accessed as list elements.

    Examples of use:
      h.robot.range.all               # returns another PyroHierarchy object
      h.robot.range.name              # return a string
      h.robot.range.all.value         # return a list of numbers
      h.robot.range[1].value          # returns a number
      h.robot.range[1:4]              # returns a list of PyroHierarchy objects
      h.devices.gripper.command = "open" # issues command "open" to gripper0

    """

    def __init__ (self, getter, setter, path=None):
        self._get = getter
        self._set = setter
        if path is None:
            path = ""
        self._path = path

        d = self.__dict__
        for i in getter(path):
            if i[-1] == '/':
                d[i[:-1]] = True
            else:
                d[i] = False

    def _make_child (self, name):
        return PyroHierarchy (self._get,
                              self._set,
                              "%s/%s" % (self._path, name))

    def __getattribute__ (self, name):
        if name[0] == '_':
            return super (PyroHierarchy, self).__getattribute__ (name)
        else:
            r = self._get('%s/%s' % (self._path, name))
            if self.__dict__.get(name):
                r = self._make_child (name)
            return r

    def __setattr__ (self, name, value):
        if name[0] == '_':
            super (PyroHierarchy, self).__setattr__ (name, value)
        else:
            self._set ("%s/%s" % (self._path, name), value)

    def __getitem__ (self, i):
        r = self._get ("%s/%s" % (self._path, i))
        if isinstance(r, list):
            r = self._make_child (i)
        return r

    def __setitem__ (self, i, value):
        return self._set ("%s/%s" % (self._path, i), value)

    def __getslice__ (self, start, end):
        return [
            self.__getitem__ (i)
            for i in xrange(start, end)
        ]

def ipyro_start (vars):
    r = vars.get('robot')
    if r :
        h = PyroHierarchy (r.get, r.set)
        vars.update ({'h':h})
    ipyro_shell(local_ns=vars)
