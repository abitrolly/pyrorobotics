#ifndef __BT848_H
#define __BT848_H

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/fcntl.h>
#include <sys/signal.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <errno.h>              /* errno */

#include "Camera.h"
#include "ioctl_meteor.h"
#include "ioctl_bt848.h" // dsb

class BT848 : public Camera
{
 public:
  BT848 ( const char* dname, int w, int h );
  void Cleanup();

 private:
  void GetData (void);
  void init(void);
  unsigned char *grab_one(int *, int *);

  int fd;
  int icontrol;
  struct meteor_counts cnt;
  char * VIDEO_DEV;
  unsigned char * buffer;
};

#endif // __BT848_H



