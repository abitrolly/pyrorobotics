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

/*
$Header$
$Log$
Revision 1.1  2003/09/15 18:45:59  dblank
New driver for B21R (elektro)

Revision 1.1.1.1  2000/07/30 15:25:52  robot
XRCL before the Austin competition

Revision 1.2  2000/07/12 03:14:33  dblank
Added GNU GPL Statement to all files

Revision 1.1  2000/03/05 01:35:34  dblank
Initial revision

Revision 1.1  2000/02/17 03:34:42  dblank
Initial revision

Revision 3.2  1999/06/24 05:00:05  dblank
Version 3.0

Revision 3.1  1999/06/24 04:40:19  dblank
Version 3.0

Revision 2.0  1999/06/05 17:10:02  dblank
Version 2.0: threads, multi-behaviors, etc.

Revision 1.4  1999/06/03 21:47:24  jrg
Worked on getting the base sonar to line up with the enclosure sonar

Revision 1.3  1999/06/01 00:58:14  jhhudso
Major Revision(s), made to work with new Sensors.h

Revision 1.2  1999/05/06 13:11:27  jrg
Added Header and Log

*/
#ifndef __VECTOR_H__
#define __VECTOR_H__

class Vector;

class Polar {
private:
	double m_daData[2];
public:
	const double &t,&r;
	Polar( void );
	Polar( const Polar & rhs);
	Polar( double dt, double dr, bool bIsPolar = true );
	Polar( const Vector & rhs );

	Polar SetCartesian( double dx, double dy );
	operator Vector( void ) const;
	Polar SetR( double dr );
	Polar SetT( double dt );
	Polar operator=( const Polar & rhs );
	Polar operator=( const Vector & rhs );
	Polar operator+( const Polar & rhs );
	Polar operator/( double val );
};

class Vector {
private:
	double m_daData[2];
public:
	const double &x,&y;

	Vector( const Vector & rhs );
	Vector( void );
	Vector( double dx, double dy, bool bIsCartesian = true );
	Vector( const Polar & rhs );

	operator Polar ( void ) const;
	Vector SetPolar( double dt, double dr );
	Vector SetX( double dx );
	Vector SetY( double dy );
	Vector SetR( double dr );
	Vector SetT( double dt );
	Vector operator=( const Polar & rhs );
	Vector operator=( const Vector & rhs );

	Vector operator+( const Vector & rhs ) const;
	Vector operator+( const double & rhs ) const;
	Vector operator-( const Vector & rhs ) const;
	Vector operator-( const double & rhs ) const;
	Vector operator-( void ) const;
	Vector operator*( const Vector & rhs ) const;
	Vector operator*( const double & rhs ) const;
	Vector operator/( const Vector & rhs ) const;
	Vector operator/( const double & rhs ) const;
	bool operator==( const Vector & rhs ) const;
	bool operator!=( const Vector & rhs ) const;

	Vector unit( void ) const;
	double norm( void ) const;
	double dot( const Vector & rhs ) const;
	double cross( const Vector & rhs ) const;
};

#endif
