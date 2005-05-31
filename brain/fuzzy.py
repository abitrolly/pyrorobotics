# Fuzzy Logic Base Class
# E. Jucovy, 2005
# based on fuzzy.py by D.S. Blank, 2001

from math import *
  
def __upMF():
  """
  A linear rising membership function
  """
  if x < a:
    return 0.0
  elif x > b:
    return 1.0
  else:
    return float(x - a) / (b - a)

def __downMF():
  """
  A linear falling membership function
  """
  if x < a:
    return 1.0
  elif x > b:
    return 0.0
  else:
    return float(b - x) / (b - a)

def __triMF():
  """
  A linear triangular membership function
  """
  if x < a:
    return 0.0
  elif x < b:
    return float(x - a) / (b - a)
  elif x < c:
    return float(c - x) / (c - b)
  else:
    return 0.0

def __trapMF():
  """
  A linear trapezoidal membership function
  """
  if x < a:
    return 0.0
  elif x < b:
    return float(x - a) / (b - a)
  elif x < c:
    return 1.0
  elif x < d:
    return float(d - x) / (d - c)
  else:
    return 0.0

def __BellMF():
  """
  I wouldn't use this yet if I were you
  """
  return 1.0 / (1.0 + pow((x - c) / a, 2.0*b))

def __SigmoidMF():
  """
  I wouldn't use this yet if I were you
  """
  return 1.0 / (1.0 + exp(-a * (x - c)))

def __GaussMF():
  """
  A Gaussian membership function
  """
  return exp(pow((float(x) - c) / s, 2.0) / -2.0)

def __LRMF():
  """
  I wouldn't use this yet if I were you
  """
  if x <= c:
    return f((c - x) / a)
  return g((x - c) / b)

class FuzzyValue:
  """
  Fuzzy value class

  Contains a floating-point value between 0 and 1
  """
  
  def __init__(self, val):
    """
    Initialize the fuzzy value

    If val is less than zero or greater than one, limit val to those bounds
    """
    
    if val < 0:
      self.Value = 0.0
    elif val > 1:
      self.Value = 1.0
    else:
      self.Value = float(val)

  def __and__(self, other):
    """
    Return the min of self and other
    """  
    return FuzzyValue(min(self.Value, float(other)))

  def __or__(self, other):
    """
    Return the max of self and other
    """
    return FuzzyValue(max(self.Value, float(other)))

  def __neg__(self):
    """
    Return 1.0 - self
    """
    return FuzzyValue(1.0 - self.Value)

  __inv__ = __neg__

  def __add__(self, other):
    return FuzzyValue(self.Value + float(other))

  __radd__ = __add__
  
  def __sub__(self, other):
    return FuzzyValue(self.Value - float(other))

  def __rsub__(self, other):
    return FuzzyValue(float(other) - self.Value)

  def __mul__(self, other):
    return FuzzyValue(self.Value * float(other))

  __rmul__ = __mul__
  
  def __div__(self, other):
    return FuzzyValue(self.Value / float(other))

  def __rdiv__(self, other):
    return FuzzyValue(float(other) / self.Value)

  def __cmp__(self, other):
    return self.Value - float(other)
  
  def __float__(self):
    return self.Value

  defuzzify = __float__

  def __str__(self):
    return "<Fuzzy value " + str(self.Value) + ">"
  
#  def alphaCut(self, alpha):
#    return self.Value >= alpha 

class FuzzyClassifier:
  """
  Fuzzy classifier class with a membership function and parameters.

  Membership function can be set on initialization or with
  setMembershipFunction(function). The membership function should
  return a value between 0 and 1; values outside that range will be
  automatically set to either 0 or 1. The function should take no
  arguments; it can access its 'arguments' by x0, x1, x2.. etc, or
  x (shorthand for x0).
  
  All relevant parameters used by the membership function can be set
  on initialization or by setParams()
  """
  
  def __init__(self, func=None, fName=None, **kwargs):
    """
    Initialize the FuzzyClassifier
    
    First argument is a dictionary of parameter names and values
    Second argument is a reference to the membership function
    Third argument is the name of the membership function
    """
    if not func is None:
      self.Function = func
    else:
      def Halfway():
        return 0.5
      self.Function = Halfway

    if not fName is None:
      self.FunctionName = fName
    else:
      self.FunctionName = self.Function.__name__

    self.myParams = kwargs
    
  def __call__(self, *args):
    """
    Apply the fuzzy classifier to a set of values

    Return a FuzzyValue with value Function(args)
    """

    # get Params and arguments (x or x0,x1..etc)
    locdict = self.myParams.copy()
    n = 0
    locdict['x'] = args[0]
    for arg in args:
      locdict['x%d'%n] = arg
      n = n + 1
    tdict = globals().copy()
    for x in locdict:
      tdict[x] = locdict[x]
    tdict['argList'] = args  #add local variable argList
    return FuzzyValue(eval(self.Function.func_code, tdict))

  def setParams(self, **kwargs):
    """
    Set one or more of the classifier's parameters
    without deleting predefined parameters
    """
    keys = kwargs.keys()
    for key in keys:
      self.myParams[key] = kwargs[key]

  def resetParams(self, **kwargs):
    """
    Set all the classifier's parameters at once and
    delete any parameters that might already exist
    """
    self.myParams = kwargs
    
  def getParam(self, name):
    """
    Return one of the classifier's parameters
    """
    return self.myParams[name]

  def setFunction(self, func, fName = None):
    """
    Set the classifier's membership function

    First (required) parameter is the membership function itself.
    This function must take no arguments; the values being applied to
    the function are stored as x (= x0), x1, x2... etc. The entire
    list of arguments can be accessed as 'argList'. The function can
    additionally use any number of parameters, which will have to be
    defined in the FuzzyClassifier.
    
    Second (optional) parameter is a name for the function, recommended,
    e.g., for lambda functions; if this is not set then the function's
    actual name will be used
    """

    self.Function = func
    if fName is None:
      self.FunctionName = func.__name__
    else:
      self.FunctionName = fName      
   
  def __str__(self):
    return "<FuzzyClassifier instance with parameters " + \
           str(self.myParams) + " and membership function " + \
           self.FunctionName + ">"
   
  def __and__ (self, other):
    """
    Return a FuzzyClassifier with the membership function
    min(self, other)
    """

    return FuzzyClassifier(min(f(*argList), g(*argList)),
                           self.FunctionName + "And" + other.FunctionName,
                           f=self, g=other)

  def __or__ (self, other):
    """
    Return a FuzzyClassifier with the membership function
    max(self, other)

    self, other must take the same arguments
    """

    return FuzzyClassifier(lambda : max(f(*argList), g(*argList)),
                           self.FunctionName + "Or" + other.FunctionName,
                           f=self, g=other)

  def __neg__(self):
    """
    Return a FuzzyClassifier with the membership function
    (1.0 - self)
    """

    return FuzzyClassifier(lambda : 1.0 - f(*argList),
                           "Not" + self.FunctionName, f=self)

  __inv__ = __neg__
         
  def __nonzero__(self):
    return True

  def __rshift__(self, val):
    """
    Return a FuzzyValue classified under a linear rising
    membership function whose parameters are decided by the
    current FuzzyClassifier's parameters

    Implemented for backwards compatibility
    """
    keys = self.myParams.keys()
    if len(keys) > 2:
      print "This may not do what you expect."
    a = self.myParams[keys[0]]
    b = self.myParams[keys[1]]
    if a > b:
      aFC = RisingFuzzy(b,a)
    else:
      aFC = RisingFuzzy(a,b)
    return aFC(val)

  def __lshift__(self, val):
    """
    Return a FuzzyValue classified under a linear falling
    membership function whose parameters are decided by the
    current FuzzyClassifier's parameters

    Implemented for backwards compatibility
    """
    keys = self.myParams.keys()
    if len(keys) > 2:
      print "This may not do what you expect."
    a = self.myParams[keys[0]]
    b = self.myParams[keys[1]]
    if a > b:
      aFC = FallingFuzzy(b,a)
    else:
      aFC = FallingFuzzy(a,b)
    return aFC(val)

def Fuzzy(a,b):
  """
  Create a new FuzzyClassifier with two parameters and
  default membership function

  Implemented for backwards compatibility
  """
  return FuzzyClassifier(a=a,b=b)

def RisingFuzzy(a,b):
  """
  Create a new FuzzyClassifier with a linear rising membership
  function and parameters a,b

  a: lower bound, mu(a) = 0.0
  b: upper bound, mu(b) = 1.0
  """
  return FuzzyClassifier(__upMF, "Rising", a=a, b=b)

def FallingFuzzy(a,b):
  """
  Create a new FuzzyClassifier with a linear falling membership
  function and parameters a,b

  a: lower bound, mu(a) = 1.0
  b: upper bound, mu(b) = 0.0
  """
  return FuzzyClassifier(__downMF, "Falling", a=a, b=b)

def TriangleFuzzy(a,b,c):
  """
  Create a new FuzzyClassifier with a linear triangular membership
  function and parameters a,b,c

  a: lower bound, mu(a) = 0.0
  b: midpoint, mu(b) = 1.0
  c: upper bound, mu(c) = 0.0
  """
  return FuzzyClassifier(__triMF, "Triangle", a=a, b=b, c=c)

def TrapezoidFuzzy(a,b,c,d):
  """
  Create a new FuzzyClassifier with a linear trapezoidal membership
  function and parameters a,b,c,d

  a: lower bound, mu(a) = 0.0
  b: start of top, mu(b) = 1.0
  c: end of top, mu(c) = 1.0
  d: upper bound, mu(d) = 0.0
  """
  return FuzzyClassifier(__trapMF, "Trapezoid", a=a, b=b, c=c, d=d)

def GaussianFuzzy(c,s):
  """
  Create a new FuzzyClassifier with a gaussian membership function
  and parameters c,s

  c: center (mean), mu(c) = 1.0
  s: spread (standard deviation)
  """
  return FuzzyClassifier(__GaussMF, "Gaussian", c=c, s=s)

def BellFuzzy(a,b,c):
  """
  Create a new FuzzyClassifier with a bell-curve membership function
  and parameters a,b,c

  I wouldn't use this yet if I were you.
  """
  
  return FuzzyClassifier(__BellMF, "BellCurve", a=a,b=b,c=c)

def SigmoidFuzzy(a,c):
  """
  Create a new FuzzyClassifier with a sigmoid membership function
  and parameters a,c

  I wouldn't use this yet if I were you.
  """
  return FuzzyClassifier(__SigmoidMF, "Sigmoid", a=a, c=c)

def LRFuzzy(f,g,c,a,b):
  """
  Create a new FuzzyClassifier with a left-right membership
  function and parameters f,g,c,a,b

  f: left-side function (actually a FuzzyClassifier)
  g: right-side function (actually a FuzzyClassifier)
  c: switching point

  This could be a lot better.
  """

  return FuzzyClassifier(__LRMF, "Left"+f.__name__+"Right"+g.__name__,
                         f=f,g=g,c=c,a=a,b=b)
    
if __name__ == '__main__': # some tests
  def Bounds():
    if x == first:
      return 0.0
    elif x == last:
      return 1
    return 0.5
  bound = FuzzyClassifier(Bounds, first=0, last=10)
  far = RisingFuzzy(0, 10)
  
  def Two():
    return one(x0) * two(x1)
  
#  foo = FuzzyClassifier(Two, one=bound, two=far)
#  print foo(10, 10)
#  nonfoo = -foo
  foo = far
  print foo(5)
  nonfoo = -foo
  print nonfoo(10)
#  print (nonfoo | foo)(10,10)
  s = GaussianFuzzy(35,5)
  print s(30)
