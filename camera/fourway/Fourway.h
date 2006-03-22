#ifndef __FOURWAY_H__
#define __FOURWAY_H__

#include "Device.h"

class Fourway : public Device {

 public:
  unsigned char *otherimage;
  int otherwidth;
  int otherheight;
  int otherdepth;
  int quadNumber;

  Fourway(void *odev, int splits, int quad);
  PyObject *updateMMap();
};

#endif
