#
# this is the geometry code. It is all R^3.
#
# All vectors/points are lists w/ 3 elements [x,y,z]
#
# Affine vectors are tuples like: ([x,y,z],[i,j,k])
#
#
# - stephen -
#

import math
TOLERANCE = .0001
PIOVER180 = math.pi / 180.0
PITIMES180 = math.pi * 180.0
DEG90RADS = 0.5 * math.pi
COSDEG90RADS = math.cos(DEG90RADS) / 1000.0
SINDEG90RADS = math.sin(DEG90RADS) / 1000.0

def distance(x1, y1, x2, y2):
    return math.sqrt( (x1 - x2) ** 2 + (y1 - y2) ** 2 )

def angleAdd(angle, degree): # angles in degrees
    return (angle + degree) % 360 # make positive, in range 0-360

def angleEqual(angle1, angle2, tolerance = 5): # angles and tolerance in degrees
    return abs((angle1 % 360)  - (angle2 % 360)) < tolerance

class Polar:
   def __init__(self, dt = 0.0, dr = 0.0, bIsPolar = 1):
      if (bIsPolar):
         self.t = dt
         self.r = dr
      else:
         self.t = math.atan2(dr,dt)
         self.r = math.sqrt(dr*dr + dt*dt)

   def setCartesian(self, dx, dy):
      self.t = math.atan2(dy,dx)
      self.r = math.sqrt(dx*dx + dy*dy)
      return self

class Vector:
   def __init__(self, d, a):
      self.distance = d
      self.angle = a

def vector():
    return [0,0,0]

def point():
    return [0,0,0]

def PrintPoint(a):
    return "(" + str(a[0]) + " ," + str(a[1]) + " ," + str(a[2])+")"

def affineVector():
    return (point(),vector())

def sub(a,b):
    c = vector()
    c[0] = a[0]-b[0]
    c[1] = a[1]-b[1]
    c[2] = a[2]-b[2]
    return c

def inverse(a):
    c = vector()
    c[0] = -a[0]
    c[1] = -a[1]
    c[2] = -a[2]
    return c

def add(a,b):
    c = vector()
    c[0] = a[0]+b[0]
    c[1] = a[1]+b[1]
    c[2] = a[2]+b[2]
    return c

def multiply(a,b):
    "a is float, b is matrix "
    c = point()
    for x in range(0,3):
        c[x] = a*b[x]
    return c

def dot(a,b, dim=3):
    sum = 0
    for x in range(0,dim):
        sum = sum + a[x]*b[x]
    return sum

def cross(a,b):
    c = vector()    
    c[0] = a[1]*b[2] - a[2]*b[1]
    c[1] = a[2]*b[0] - a[0]*b[2]
    c[2] = a[0]*b[1] - a[1]*b[0]
    return c

def norm(a):
    return math.sqrt(dot(a,a))

def normalize(a, dim = 3):
    b = vector()
    l = norm(a)
    for x in range(0,dim):
        b[x] = a[x]/l
    return b

def angle(a,b=[1,0,0]):
    #print "angle", a, b
    return math.acos(dot(normalize(a),normalize(b)))

def toleq(a,b):
    if abs(a-b) > TOLERANCE:
        return 0
    return 1

"""
These are the intersect functions
added by Muhammad temporary
Stephen - please rewrite them, optimize them, or I don't know - do something
"""

def intersectSegSeg(A0, A1, B0, B1):
    #return (intersect?, D)
    #intersect? is 0 if not, 1 it yes
    #D is the intersectin point
    (inter1, d) = intersectLineSeg(A0, A1, B0, B1)
    (inter2, d) = intersectLineSeg(B0, B1, A0, A1)
    return (inter1 * inter2, d)

def intersectLineSeg( L0,  L1, S0, S1):
    L0 = map (float, L0)
    L1 = map (float, L1)
    S0 = map (float, S0)
    S1 = map (float, S1)
    #return (intersect?, D)
    #intersect? is 0 if not, 1 it yes
    #D is the intersectin point
    
    #print L0, L1, S0, S1
    if((S0[0] == S1[0]) and (S0[1] == S1[1])): #we only test real lines
        return (0, [0,0])
    if((L0[0] == L1[0]) and (L0[1] == L1[1])):
        return (0, [1,0])
    
    nL = [-(L1[1] - L0[1]), L1[0] - L0[0]]
    #nL = [L1[0] - L0[0], L1[1] - L0[1]]
    dS = [ S1[0] - S0[0], S1[1] - S0[1]]
    
    nd = -dot(nL,dS, 2)
    
    if(toleq(nd,0)):
        return (0, [2, 0])
    
    dLS = [S0[0] - L0[0], S0[1] - L0[1]]
    
    #print nL
    #print dS
    #print dLS
    t = dot(nL,dLS, 2) / nd
    
    if(t < 0):
        return (0, [0, -1])
    
    if(t > 1):
        return (0, [0, 1])
    
    D = [t*dS[0] + S0[0], t*dS[1] + S0[1]]
    
    return (1, D)

def distance2(a, b):
    c = sub(a,b)
    return dot(c,c)
	
def pol2car(ang, length):#2d
    return [math.cos(ang)*length, math.sin(ang)*length, 0]

def rotate(vec, ang):#2d
    if (ang==0):
        return vec
    if (norm(vec) ==0):	#length of vec is 0!
        return vec
    #print "rotate",vec, ang
    return pol2car(angle(vec) + ang, dot(vec, vec))

if __name__ == '__main__':
    print math.sqrt(9)
    x1 = [1,0,0]
    x2 = [0,1,0]
    x3 = [0,0,1]
    a  = [1,1,1]
    b  = [-1,1,2]
    
    if not toleq(angle(x1,x2),math.pi/2):
        print "angle is broken ",angle(x1,x2)," insted of ",math.pi/2
        
    if cross(x1,x2) != x3:
        print "cross is broken"

    print intersectSegSeg([0,0],[2,2],[2,0],[0,2])
