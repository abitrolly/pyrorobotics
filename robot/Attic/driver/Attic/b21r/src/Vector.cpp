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

#include <math.h>
#include "Vector.h"

Polar::Polar( const Polar & rhs)
	: t(m_daData[0]),r(m_daData[1])
{
	m_daData[0] = rhs.t;
	m_daData[1] = rhs.r;
}

Polar::Polar( void )
	: t(m_daData[0]),r(m_daData[1])
{
	m_daData[0] = 0.0;
	m_daData[1] = 0.0;
}

Polar::Polar( double dt, double dr, bool bIsPolar ) 
	: t(m_daData[0]),r(m_daData[1])
{
	if (bIsPolar) {
		m_daData[0] = dt;
		m_daData[1] = dr;
	} else {
		m_daData[0] = atan2(dr,dt);
		m_daData[1] = sqrt(dr*dr + dt*dt);
	}
}

Polar::Polar( const Vector & rhs )
	: t(m_daData[0]),r(m_daData[1])
{
		m_daData[0] = atan2(rhs.y,rhs.x);
		m_daData[1] = sqrt(rhs.x*rhs.x + rhs.y*rhs.y);
}

Polar Polar::SetCartesian( double dx, double dy )
{
	m_daData[0] = atan2(dy,dx);
	m_daData[1] = sqrt(dx*dx + dy*dy);

	return *this;
}

/*
Polar::operator Vector( void ) const
{
	return Vector(
		r * cos ( t ),
		r * sin ( t )
	);
}
*/

Polar Polar::SetR( double dr )
{
	m_daData[1] = dr;

	return *this;
}

Polar Polar::SetT( double dt )
{
	m_daData[0] = dt;

	return *this;
}

/*
Polar Polar::operator=( const Polar & rhs )
{
	m_daData[0] = rhs.t;
	m_daData[1] = rhs.r;

	return * this;
}

Polar Polar::operator=( const Vector & rhs )
{
	SetCartesian(rhs.x,rhs.y);

	return *this;
}
*/

Polar Polar::operator+( const Polar & rhs )
{
  double x = 0,
         y = 0;
  
  x = (rhs.r * cos ( rhs.t )) + ( m_daData[1] * cos ( m_daData[0] ) );
  y = (rhs.r * sin ( rhs.t )) + ( m_daData[1] * sin ( m_daData[0] ) );

  return Polar(
	       atan2( y, x ),
	       sqrt( x*x + y*y )
	       );
}

Polar Polar::operator/( double val )
{
  double x = 0,
         y = 0;
  
  x = ( m_daData[1] * cos ( m_daData[0] ) )/val;
  y = ( m_daData[1] * sin ( m_daData[0] ) )/val;

  return Polar(
	       atan2( y, x ),
	       sqrt( x*x + y*y )
	       );
}


/****************************************************************************/
Vector::Vector( const Vector & rhs )
	: x(m_daData[0]),y(m_daData[1])
{
	m_daData[0] = rhs.x;
	m_daData[1] = rhs.y;
}

Vector::Vector( void )
	: x(m_daData[0]),y(m_daData[1])
{
	m_daData[0] = 0;
	m_daData[1] = 0;
}

Vector::Vector( double dx, double dy, bool bIsCartesian)
	:x(m_daData[0]),y(m_daData[1])
{
	if (bIsCartesian) {
		m_daData[0] = dx;
		m_daData[1] = dy;
	} else {
		m_daData[0] = dy * cos ( dx );
		m_daData[1] = dy * sin ( dx );
	}
}

Vector::Vector( const Polar & rhs )
	:x(m_daData[0]),y(m_daData[1])
{
		m_daData[0] = rhs.r * cos ( rhs.t );
		m_daData[1] = rhs.r * sin ( rhs.t );
}

/*
Vector::operator Polar ( void ) const
{
	return Polar(
		atan2(y,x),
		sqrt(x*x + y*y)
	);
}
*/

Vector Vector::SetPolar( double dt, double dr )
{
	m_daData[0] = dr * cos ( dt );
	m_daData[1] = dr * sin ( dt );

	return *this;
}

Vector Vector::SetX( double dx )
{
	m_daData[0] = dx;

	return *this;
}

Vector Vector::SetY( double dy )
{
	m_daData[1] = dy;

	return *this;
}

Vector Vector::SetR( double dr )
{
	double theta;

	theta = atan2(y,x);

	m_daData[0] = dr * cos ( theta );
	m_daData[1] = dr * sin ( theta );

	return *this;
}

Vector Vector::SetT( double dt )
{
	double radius;

	radius = sqrt(x*x + y*y);

	m_daData[0] = radius * cos( dt );
	m_daData[1] = radius * sin( dt );

	return *this;
}

/*
Vector Vector::operator=( const Polar & rhs )
{
	SetPolar(rhs.t,rhs.r);
	return *this;
}

Vector Vector::operator=( const Vector & rhs )
{
	m_daData[0] = rhs.x;
	m_daData[1] = rhs.y;

	return *this;
}
*/

Vector Vector::operator+( const Vector & rhs ) const
{
	return Vector(x+rhs.x,y+rhs.y);
}

Vector Vector::operator+( const double & rhs ) const
{
	return Vector(x+rhs,y+rhs);
}

Vector Vector::operator-( const Vector & rhs ) const
{
	return Vector(x-rhs.x,y-rhs.y);
}

Vector Vector::operator-( const double & rhs ) const
{
	return Vector(x-rhs,y-rhs);
}

Vector Vector::operator-( void ) const
{
	return Vector(-x,-y);
}

Vector Vector::operator*( const Vector & rhs ) const
{
	return Vector(x*rhs.x,y*rhs.y);
}

Vector Vector::operator*( const double & rhs ) const
{
	return Vector(x*rhs,y*rhs);
}

Vector Vector::operator/( const Vector & rhs ) const
{
	return Vector(x/rhs.x,y/rhs.y);
}

Vector Vector::operator/( const double & rhs ) const
{
	return Vector(x/rhs,y/rhs);
}

bool Vector::operator==( const Vector & rhs ) const
{
	return x == rhs.x && y == rhs.y;
}

bool Vector::operator!=( const Vector & rhs ) const
{
	return x != rhs.x || y != rhs.y;
}

Vector Vector::unit( void ) const
{
	double radius;

	radius = sqrt (x*x + y*y);

	if (radius == 0.0) 
		return Vector(0,0);

	return Vector (x/radius,y/radius);
}

double Vector::norm( void ) const
{
	return sqrt(x*x + y*y);
}

double Vector::dot( const Vector & rhs ) const
{
	return x*rhs.x + y*rhs.y;
}

double Vector::cross( const Vector & rhs ) const
{
	return x*rhs.y - rhs.x*y;
}
