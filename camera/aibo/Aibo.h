#ifndef __AIBO_H__
#define __AIBO_H__

#include "Device.h"
#include "Socket.h"

class Aibo : public Device {
 public:
  Aibo(char *hostname);
  PyObject *updateMMap(int decompress);
  Socket *sock;
};

#endif
