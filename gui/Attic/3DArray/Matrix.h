#ifndef __MATRIX_H__
#define __MATRIX_H__

class Vertex3D {
 private:
  friend class Matrix;
  double data[3];
 public:
  const double & x, & y, & z;
  
  Vertex3D(const Vertex3D & rhs) 
    : x(data[0]),y(data[1]),z(data[2]) 
    { data[0]=rhs.x;data[1]=rhs.y;data[2]=rhs.z;  }
  Vertex3D(void)
    : x(data[0]),y(data[1]),z(data[2]) 
    { data[0] = data[1] = data[2] = 0.0; }
  Vertex3D(double x0,double y0,double z0)
    : x(data[0]),y(data[1]),z(data[2]) 
    { data[0] = x0;data[1]=y0;data[2]=z0; }
  Vertex3D & operator=(const Vertex3D & rhs) 
  { data[0]=rhs.x;data[1]=rhs.y;data[2]=rhs.z; 
  return *this;}
  
  Vertex3D operator + (const Vertex3D & v)
    { return Vertex3D(x+v.x,y+v.y,z+v.z); }
  Vertex3D operator - (const Vertex3D & v)
    { return Vertex3D(x-v.x,y-v.y,z-v.z); }
  Vertex3D operator * (const double d)
    { return Vertex3D(x*d,y*d,z*d); }
  
  Vertex3D Unit(void);
  double dot(const Vertex3D & rhs)
    { return x*rhs.x + y*rhs.y + z*rhs.z; }
};

class Matrix {
 private:
  double matrix[4][4];
  const static double rad;
 public:
  Matrix(
	 double x0, double y0, double z0, double w0,
	 double x1, double y1, double z1, double w1,
	 double x2, double y2, double z2, double w2,
	 double x3, double y3, double z3, double w3
	 );
  
  Matrix(void);
  
  Matrix Multiply(const Matrix & m);
  Vertex3D Multiply(const Vertex3D & v);
  Matrix operator * (const Matrix & m) { return Multiply(m); }
  Vertex3D operator * (const Vertex3D & v) { return Multiply(v); }
  
  static Matrix RotateXDeg(double rot);
  static Matrix RotateXRad(double rot);
  static Matrix RotateYDeg(double rot);
  static Matrix RotateYRad(double rot);
  static Matrix RotateZDeg(double rot);
  static Matrix RotateZRad(double rot);
  static Matrix Translate(double x,double y,double z);
  static Matrix Scale(double x,double y,double z);
  Matrix Inverse( );
};

#endif
