#include <math.h>
#include "Matrix.h"

const double Matrix::rad = 3.141592653589/180.0;
/*======================================================================
======================================================================*/

Matrix::Matrix(
	       double x0, double y0, double z0, double w0,
	       double x1, double y1, double z1, double w1,
	       double x2, double y2, double z2, double w2,
	       double x3, double y3, double z3, double w3
	       ) {
  matrix[0][0] = x0;
  matrix[1][0] = y0;
  matrix[2][0] = z0;
  matrix[3][0] = w0;
  
  matrix[0][1] = x1;
  matrix[1][1] = y1;
  matrix[2][1] = z1;
  matrix[3][1] = w1;
  
  matrix[0][2] = x2;
  matrix[1][2] = y2;
  matrix[2][2] = z2;
  matrix[3][2] = w2;
  
  matrix[0][3] = x3;
  matrix[1][3] = y3;
  matrix[2][3] = z3;
  matrix[3][3] = w3;
}

/*======================================================================
  ======================================================================*/
Matrix::Matrix( ) 
{
  *this = Matrix(
		 1.0, 0.0, 0.0, 0.0,
		 0.0, 1.0, 0.0, 0.0,
		 0.0, 0.0, 1.0, 0.0,
		 0.0, 0.0, 0.0, 1.0
		 );
}

/*======================================================================
  ======================================================================*/
Matrix Matrix::Multiply(const Matrix & m)
{
  Matrix result;
  
  for (int i=0;i<4;i++)
    for (int j=0;j<4;j++) {
      result.matrix[i][j] = 0.0;
      for (int k=0;k<4;k++)
	result.matrix[i][j] += matrix[k][j] * m.matrix[i][k];
    }
  return result;
}

Vertex3D Vertex3D::Unit(void)
{
  double scale;
  scale = sqrt (x*x + y*y + z*z);
  return  Vertex3D(x/scale,y/scale,z/scale);
}  

/*======================================================================
  A fairly fast vertex-matrix multiply
  Not really interested in the w term since since we're not doing
  any kind of perspective adjustment with the matrix
  ======================================================================*/
Vertex3D Matrix::Multiply(const Vertex3D & v)
{
  Vertex3D result;
  
  result.data[0] = matrix[0][0]*v.x + matrix[1][0]*v.y + matrix[2][0]*v.z + 
    matrix[3][0];
  result.data[1] = matrix[0][1]*v.x + matrix[1][1]*v.y + matrix[2][1]*v.z + 
    matrix[3][1];
  result.data[2] = matrix[0][2]*v.x + matrix[1][2]*v.y + matrix[2][2]*v.z + 
    matrix[3][2];
  
  return result;
}


/*======================================================================
  RotateX
  This method creates a rotation matrix that rotates around the
  X axis
  ======================================================================*/
Matrix Matrix::RotateXDeg(double rot)
{
  return RotateXRad(rot*rad);
}

Matrix Matrix::RotateXRad(double rot)
{
  double s = sin(rot);
  double c = cos(rot);
  Matrix result (
		 1.0,    0.0,	0.0,   0.0,
		 0.0,      c,     -s,   0.0,
		 0.0,      s,      c,   0.0,
		 0.0,    0.0,    0.0,   1.0
		 );
  
  return result;			
}

/*======================================================================
  RotateY
  This method creates a rotation matrix that rotates around the
  Y axis
  ======================================================================*/
Matrix Matrix::RotateYDeg(double rot)
{
  return RotateYRad(rot*rad);
}

Matrix Matrix::RotateYRad(double rot)
{
  double s = sin(rot);
  double c = cos(rot);
  Matrix result(
		c,    0.0,      s,   0.0,
		0.0,    1.0,    0.0,   0.0,
		-s,    0.0,      c,   0.0,
		0.0,    0.0,    0.0,   1.0
		);
  
  return result;			
}

/*======================================================================
  RotateY
  This method creates a rotation matrix that rotates around the
  Y axis
  ======================================================================*/
Matrix Matrix::RotateZDeg(double rot)
{
  return RotateZRad(rot*rad);
}

Matrix Matrix::RotateZRad(double rot)
{
  double s = sin(rot);
  double c = cos(rot);
  Matrix result (
		 c,     -s,    0.0,   0.0,
		 s,      c,    0.0,   0.0,
		 0.0,    0.0,    1.0,   0.0,
		 0.0,    0.0,    0.0,   1.0
		 );
  
  return result;			
}

/*======================================================================
  Translate the matrix
  ======================================================================*/
Matrix Matrix::Translate(double x,double y,double z)
{
  Matrix result (
		 1.0, 0.0, 0.0, x,
		 0.0, 1.0, 0.0, y,
		 0.0, 0.0, 1.0, z,
		 0.0, 0.0, 0.0, 1.0
		 );
  return result;
}

/*======================================================================
  Scale the matrix
  ======================================================================*/

Matrix Matrix::Scale(double x,double y,double z)
{
  Matrix result (
		 x,   0.0, 0.0, 0.0,
		 0.0, y,   0.0, 0.0,
		 0.0, 0.0, z,   0.0,
		 0.0, 0.0, 0.0, 1.0
		 );
  return result;
}

/*======================================================================
  Calculate the inverse matrix, good for going from screen coords to
  world coords
  ======================================================================*/
Matrix Matrix::Inverse( )
{
  Matrix result;
  //double m[4][4] = result.matrix;
  double m[4][4] = { {0.0} };
  double det;
  double d21, d31, d32, d42, d43, d14;
  
  d21 = (matrix[0][2]*matrix[1][3]-matrix[0][3]*matrix[1][2]);
  d31 = (matrix[0][2]*matrix[2][3]-matrix[0][3]*matrix[2][2]);
  d32 = (matrix[1][2]*matrix[2][3]-matrix[1][3]*matrix[2][2]);
  d42 = (matrix[1][2]*matrix[3][3]-matrix[1][3]*matrix[3][2]);
  d43 = (matrix[2][2]*matrix[3][3]-matrix[2][3]*matrix[3][2]);
  d14 = (matrix[3][2]*matrix[0][3]-matrix[3][3]*matrix[0][2]);
  
  m[0][0] =  (matrix[1][1] * d43 - matrix[2][1] * d42 + matrix[3][1] * d32);
  m[0][1] = -(matrix[0][1] * d43 + matrix[2][1] * d14 + matrix[3][1] * d31);
  m[0][2] =  (matrix[0][1] * d42 + matrix[1][1] * d14 + matrix[3][1] * d21);
  m[0][3] = -(matrix[0][1] * d32 - matrix[1][1] * d31 + matrix[2][1] * d21);
  
  det = matrix[0][0] * m[0][0] + matrix[1][0] * m[0][1] + matrix[2][0] * m[0][2] + matrix[3][0] * m[0][3];
  
  if (det == 0.0) 
    return Matrix( );
  double invDet = 1.0 / det;
  
  m[0][0] *= invDet;
  m[0][1] *= invDet;
  m[0][2] *= invDet;
  m[0][3] *= invDet;
  
  m[1][0] = -(matrix[1][0] * d43 - matrix[2][0] * d42 + matrix[3][0] * d32) * invDet;
  m[1][1] =  (matrix[0][0] * d43 + matrix[2][0] * d14 + matrix[3][0] * d31) * invDet;
  m[1][2] = -(matrix[0][0] * d42 + matrix[1][0] * d14 + matrix[3][0] * d21) * invDet;
  m[1][3] =  (matrix[0][0] * d32 - matrix[1][0] * d31 + matrix[2][0] * d21) * invDet;
  
  d21 = matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0];
  d31 = matrix[0][0]*matrix[2][1]-matrix[0][1]*matrix[2][0];
  d32 = matrix[1][0]*matrix[2][1]-matrix[1][1]*matrix[2][0];
  d42 = matrix[1][0]*matrix[3][1]-matrix[1][1]*matrix[3][0];
  d43 = matrix[2][0]*matrix[3][1]-matrix[2][1]*matrix[3][0];
  d14 = matrix[3][0]*matrix[0][1]-matrix[3][1]*matrix[0][0];
  
  m[2][0] =  (matrix[1][3] * d43 - matrix[2][3] * d42 + matrix[3][3] * d32) * invDet;
  m[2][1] = -(matrix[0][3] * d43 + matrix[2][3] * d14 + matrix[3][3] * d31) * invDet;
  m[2][2] =  (matrix[0][3] * d42 + matrix[1][3] * d14 + matrix[3][3] * d21) * invDet;
  m[2][3] = -(matrix[0][3] * d32 - matrix[1][3] * d31 + matrix[2][3] * d21) * invDet;
  m[3][0] = -(matrix[1][2] * d43 - matrix[2][2] * d42 + matrix[3][2] * d32) * invDet;
  m[3][1] =  (matrix[0][2] * d43 + matrix[2][2] * d14 + matrix[3][2] * d31) * invDet;
  m[3][2] = -(matrix[0][2] * d42 + matrix[1][2] * d14 + matrix[3][2] * d21) * invDet;
  m[3][3] =  (matrix[0][2] * d32 - matrix[1][2] * d31 + matrix[2][2] * d21) * invDet;
  
  return result; 		
}

