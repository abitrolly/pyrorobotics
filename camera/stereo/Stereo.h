#ifndef __STEREO_H__
#define __STEREO_H__

#include "Device.h"

class Stereo : public Device {

 public:
  unsigned char *leftimage;
  unsigned char *rightimage;
  int leftwidth;
  int leftheight;
  int leftdepth;
  int rightwidth;
  int rightheight;
  int rightdepth;

  Stereo(void *left, void *right);
  PyObject *updateMMap();
};

#endif
