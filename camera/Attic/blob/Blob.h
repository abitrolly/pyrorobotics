#ifndef __BLOB_H__
#define __BLOB_H__

#include "Device.h"

class Blob : public Device {

 public:
  Blob(char filename[]);
  PyObject *updateMMap(char filename[]);
};

#endif
