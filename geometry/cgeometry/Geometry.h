#ifndef __GEOMETRY_H__
#define __GEOMETRY_H__

#include <Python.h>
#include <stdlib.h>
#include <math.h>

class Geometry {
 public:
  Geometry();
};

class Segment {
 public:
  int x1, y1, x2, y2;
  int id;
  Segment(int x1, int y1, int x2, int y2, int id);
  double length();
  bool in_bbox(int x, int y);
  bool parallel(Segment other);
  bool vertical(Segment other);
  bool intersection(Segment other);
  PyObject *intersects(Segment other);
  double yintercept();
};

#endif 
