#ifndef __BLOB_H__
#define __BLOB_H__

#include "Device.h"

class Blob : public Device {

 public:
  Blob(int w, int h, int d);
  PyObject *updateMMap(PyObject *blobData);
};

#endif
