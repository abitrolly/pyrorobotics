#ifndef __3DGRAPHICS_H__
 #define __3DGRAPHICS_H__

#include "RobotDrawTypes.h"
#include "Matrix.h"

class PolygonHolder {
 public:
  TCArray <Vertex3D,Vertex3D &> points;
  double z;
  double r,g,b;
  PolygonHolder():z(0),r(0),g(0),b(0){}
};

class 3DGraphics {
 private:
  long mousex,mousey;
  long mouse_x, mouse_y;
  Matrix RotateMatrixRobot;
  Matrix RotateMatrixWorld;
  int m_Button;
  
  Vertex3D m_Frustum[4];
  double scale;
  
  TCArray <PolygonHolder *,PolygonHolder *> PolygonList;
  
 public:
  bool m_bDoubleBuffer;
  bool m_bSolidPolygons;
  3DGraphics();
  void paintEvent ( );
  void mousePressEvent( );
  void mouseMoveEvent( );
  
  void AddPerspective(Vertex3D & vert );
  
  
  void SortPolygonList(void);	
  void SortPolygonList(Vertex3D polylist[180], int);
  void SetSize(int width,int height );
  void ClipFace( const Vertex3D * verticies,long count, Vertex3D * result, 
		 long & resultcount);
};

#endif
