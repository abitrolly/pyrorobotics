#ifndef _CANVAS3D_H_
#define _CANVAS3D_H_

#include "Matrix.h"
#include "simple_templates.h"

class RGB {
 public:
  int red;
  int green;
  int blue;
  RGB(int r, int g, int b) {
    red = r;
    green = g;
    blue = b;
  }
  void set(int r, int g, int b) {
    red = r;
    green = g;
    blue = b;
  }
  void set(RGB *rgb) {
    red = rgb->red;
    green = rgb->green;
    blue = rgb->blue;
  }
  bool same(RGB *right) {
    return (right->red == red &&
	    right->green == green &&
	    right->blue == blue);
  }
  bool same(RGB &right) {
    return (right.red == red &&
	    right.green == green &&
	    right.blue == blue);
  }
};

class PolygonHolder {
 public:
  TCArray <Vertex3D,Vertex3D &> points;
  double z;
  double r,g,b;
  PolygonHolder():z(0),r(0),g(0),b(0){}
};

class Canvas3D {
 public:
  static const int POINT = 0;
  static const int LINE = 1;
  static const int COLOR = 2;
  static const int LINE_WIDTH = 3;
  static const int FILL = 4;
  // Methods:
  Canvas3D(int w, int h, char buffer[], int r);
  void AddPerspective(Vertex3D & vert );
  void ClipFace(const Vertex3D * verticies,long count, 
			  Vertex3D * result, long & resultcount);
  void SetSize(int width,int height );
  void fill(int x, int y);
  void draw_line(int x1, int y1, int x2, int y2);
  void draw_point(int x1, int y1);
  RGB *getPixel(int x, int y);
  void setPixel(int x, int y);
  // Public vars:
  char *buf;
  int rowstride;
  int red, green, blue;
  int line_width;
  int width, height;
  double scale;
  Vertex3D m_Frustum[4];
};

#endif
