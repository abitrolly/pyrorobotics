#ifndef __AIBO_H__
#define __AIBO_H__

#define SWAP(a,b) { int itemp=(a);(a)=(b);(b)=itemp;}
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))

#include "Device.h"

class Aibo : public Device {
 public:
  Aibo(int w, int h, int d);
  PyObject *updateMMap(PyObject *points, PyObject *lines);
  void clear();
  void setPixel(int x, int y, int r, int g, int b);
  void drawLine(long int x1, long int y1, 
		long int x2, long int y2, 
		long int r, long int g, long int b);
  void drawRect(long int x1, long int y1, 
		long int x2, long int y2, 
		long int r, long int g, long int b);
};

#endif
