#ifndef __FAKE_H__
#define __FAKE_H__

#include "Device.h"

class Fake : public Device {

 public:
  Fake(char filename[]);
  Fake(int w, int h, int d);
  PyObject *updateMMap(char filename[]);
};

#endif
