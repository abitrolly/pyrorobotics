#ifndef __V4L_H__
#define __V4L_H__

#include <Python.h>
#include "v4lcap.h"
#include "../vision/Vision.h"

class V4L : public Vision {

 public:
  V4L(char *device_name, int wi, int he, int de, int ch);
  void updateMMap();

  struct image_cap *v4ldev;
  int channel;
  char *device;
};

#endif
