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

#ifndef __B21RCAMMOVER_H
#define __B21RCAMMOVER_H

#include "CamMover.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <sys/fcntl.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

#define ROCKETPORT "/dev/cur1" // was ttyS1 // was cur1

class B21RCamMover : public CamMover
{
 public:
  B21RCamMover ();
  ~B21RCamMover ();

  void Init();
  void Pan(int);
  void Tilt(int);
  void PanTilt(int, int);
  void Zoom(int);

  int Up();
  int Down();
  int Left();
  int Right();

  void Center();
  int Read();
  int num_chars();

 private:
  int xpmin, ypmin, xpmax, ypmax;
  int xpos, ypos, pos;
  int rocketport;
  char buffer [80];  
};

#endif // __B21RCAMMOVER_H
