#ifndef __VISION_H__ 
#define __VISION_H__ 

#include <Python.h>

class Vision {
  static const int RED = 0;
  static const int GREEN = 1;
  static const int BLUE = 2;
  
public:
  Vision();
  Vision(int w, int h, int d, int r, int g, int b);
  ~Vision();
  void initialize(int wi, int he, int de, int r, int g, int b);
  void superColor(float w1, float w2, float w3,
		  int outChannel);
  void filterByColor(int lr, int lg, int lb,
		     int hr, int hg, int hb,
		     int outChannel);
  void filterByColor(int r, int g, int b, int tolerance, 
		     int outChannel);
  PyObject *get(int w, int h);
  PyObject *set(int w, int h, int d, int val);

  int getWidth();
  int getHeight();
  int getDepth();
  int saveImage(char filename[]);
  PyObject *getMMap();


 protected:
  int width;
  int height;
  int depth;
  int rgb[3];
  unsigned char *image;
};

#endif
