from math import atan2, sqrt

#Polar::Polar( const Polar & rhs)
#	: t(m_daData[0]),r(m_daData[1])
#{
#	m_daData[0] = rhs.t;
#	m_daData[1] = rhs.r;
#}

class Polar:
   def __init__(self, dt = 0.0, dr = 0.0, bIsPolar = 1):
      if (bIsPolar):
         self.t = dt
         self.r = dr
      else:
         self.t = atan2(dr,dt)
         self.r = sqrt(dr*dr + dt*dt)


   #Polar::Polar( const Vector & rhs )
   #	: t(m_daData[0]),r(m_daData[1])
   #{
   #		m_daData[0] = atan2(rhs.y,rhs.x);
   #		m_daData[1] = sqrt(rhs.x*rhs.x + rhs.y*rhs.y);
   #}

   def setCartesian(self, dx, dy):
      self.t = atan2(dy,dx)
      self.r = sqrt(dx*dx + dy*dy)
      return self

#Polar::operator Vector( void ) const
#{
#	return Vector(
#		r * cos ( t ),
#		r * sin ( t )
#	);
#}


#Polar Polar::SetR( double dr )
#{
#	m_daData[1] = dr;
#
#	return *this;
#}

#Polar Polar::SetT( double dt )
#{
#	m_daData[0] = dt;
#
#	return *this;
#}

#Polar Polar::operator=( const Polar & rhs )
#{
#	m_daData[0] = rhs.t;
#	m_daData[1] = rhs.r;
#
#	return * this;
#}

#Polar Polar::operator=( const Vector & rhs )
#{
#	SetCartesian(rhs.x,rhs.y);
#
#	return *this;
#}

#Polar Polar::operator+( const Polar & rhs )
#{
#  double x = 0,
#         y = 0;
#  
#  x = (rhs.r * cos ( rhs.t )) + ( m_daData[1] * cos ( m_daData[0] ) );
#  y = (rhs.r * sin ( rhs.t )) + ( m_daData[1] * sin ( m_daData[0] ) );
#
#  return Polar(
#	       atan2( y, x ),
#	       sqrt( x*x + y*y )
#	       );
#}

#Polar Polar::operator/( double val )
#{
#  double x = 0,
#         y = 0;
  
#  x = ( m_daData[1] * cos ( m_daData[0] ) )/val;
#  y = ( m_daData[1] * sin ( m_daData[0] ) )/val;

#  return Polar(
#	       atan2( y, x ),
#	       sqrt( x*x + y*y )
#	       );
#}

