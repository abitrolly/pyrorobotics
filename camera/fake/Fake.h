#ifndef __FAKE_H__
#define __FAKE_H__

#include "Device.h"

class Fake : public Device {

 public:
  Fake(char filename[]);
  PyObject *updateMMap(char filename[]);
};

#endif
