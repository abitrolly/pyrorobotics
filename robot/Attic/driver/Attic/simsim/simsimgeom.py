

class Plane:
   def __init__(self,A,B,C,D):
      """
      create a Plane given it's coeficents:
      Ax + By + Cz = D
      """
      self.normal[0] = A
      self.normal[1] = B
      self.normal[2] = C
      self.normal = normalize(self.normal)
      self.D = D
      
   def __init__(self,triangle):
      """
      initialize a Plane given a triangle. The resultant
      Plane will contain the triangle passed.
      """
      //A,B,C are the normal
      self.normal = cross(triangle.points[1]-triangle.points[0],
                     triangle.points[2]-triangle.points[0])

      self.D = 0
      for dim in range(0,3):
         self.D = self.D + self.normal[dim] * triangle.points[0][dim]

   def intersectRay(self,ray):
      """
      returns tuple:
      (point of intersection,distance to intersection)
	this code has problems.
      """
      denomonator = dot(ray[1],self.normal)
      neumerator  = self.D - dot((ray[0]+ray[1]),N)
      if denomonator <= 0:
         return None
      else return (t*ray[0]+ray[1],t)


class Triangle:
   def __init__(self,pa,pb,pc):
      self.points = [pa,pb,pc]

   def intersectRay(ray):
      """
      given a ray determine if it intersects this triangle.
      returns (point of intersection, distance to intersection)
      """
      #first see if it hits the plane we are contained in
      plane = Plane(self)
      plane.intersectRay()
      pass

   
class Shape:
   def __init__():
      pass
   
   def intersectRay(ray):
      pass

   def intersectTriangle(triangle):
      pass


class TriangleShape(Shape):
   
   def__init__(self,triList):
      """
      constructor that takes a reference to self and a list of triangles.
      """
      self.triangleList = triList
      
   def intersectRay(self,ray):
      """
      intersect a ray with every triangle return a tuple:
      (triangle of intersection(point of intersection,distance of intersection))
      None if no intersection occurs
      """
      closest = None
      for tri in self.triangleList:
         intersection = tri.intersectRay(ray)
         if intersection != None:
            if closest == None:
               closest = (x,intersection)
            else:
               if intersection[1] < closest[1][1]:
                  closest = intersection

      return closest
         
    
   def intersectTriangle(self,triangle):
      pass

class Plane(TriangleShape):
   def __init__(self,center,normal,length):
      pass

class Cube(TriangleShape):
   def __init__(center,size):
      pass

