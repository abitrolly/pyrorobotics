/*
  XRCL: The Extensible Robot Control Language
  (c) 2000, Douglas S. Blank
  University of Arkansas, Roboticists Research Group
  http://ai.uark.edu/xrcl/
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
  02111-1307, USA.

  As a special exception, you have permission to link this program
  with the Qt library and distribute executables, as long as you
  follow the requirements of the GNU GPL in regard to all of the
  software in the executable aside from Qt.
*/

#ifndef __BT848_H
#define __BT848_H

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



