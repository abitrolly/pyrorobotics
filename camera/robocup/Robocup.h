#ifndef __ROBOCUP_H__
#define __ROBOCUP_H__

#include "Device.h"

class Robocup : public Device {

 public:
  Robocup(int w, int h, int d);
  void clear();
  PyObject *updateMMap(PyObject *robocupData);
  void drawRect(long int left, long int right, 
		long int top, long int bottom, 
		long int r, long int g, long int b);
};

#endif
