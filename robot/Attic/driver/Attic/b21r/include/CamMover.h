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

#ifndef __CAMMOVER_H
#define __CAMMOVER_H

class CamMover
{
 public:
  CamMover ();
  virtual ~CamMover ();

  virtual void Init();
  virtual void Pan(int);
  virtual void Tilt(int);
  virtual void PanTilt(int, int);
  virtual void Zoom(int);
  virtual void Center();

  double PanAngle;
  double TiltAngle;
  double ZoomAmount;
};

#endif // __CAMMOVER_H