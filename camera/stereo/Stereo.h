#ifndef __STEREO_H__
#define __STEREO_H__

#include "Device.h"

class Stereo : public Device {

 public:
  unsigned char *otherimage;
  int otherwidth;
  int otherheight;
  int otherdepth;
  int quadNumber;

  Stereo(void *odev, int splits, int quad);
  PyObject *updateMMap();
};

#endif
