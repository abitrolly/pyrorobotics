#include "Sensor.h"

#include <math.h>
#include <stdio.h>

const double Sensor::DZERO      = (double)0.0;
const float Sensor::FZERO      = (float)0.0;
const int   Sensor::ZERO       = 0;
const int   Sensor::NEGONE     = -1;
const int   Sensor::MAXHISTLEN = 50;

double Sensor::P2D (double dCoord) 
  // Polar to Degrees
  // Slow, but let's double check everything before we 
  // optimize. DSB
{
  return degWrap((dCoord / PI) * 180.0);
}

double Sensor::degWrap( double dAngle )
  // Degree wrap-around
{
  double temp=(double) (((int) dAngle) % ((int)360) + (dAngle - (int) dAngle));
  while (temp < 0)
    temp += 360;
  return temp;
}

int Sensor::posWrap( int iPos, int SensorCount = 24)
  // , int SensorCount ) FIX
  // Sonar count wrap-around
{
  // FIX: pass in sensor count
  int temp = (iPos % SensorCount);
  while (temp < 0)
    temp += SensorCount;
  return temp;
}

double Sensor::seglen( double ox, double oy, double ex, double ey ) {
  return sqrt((ex - ox)*(ex - ox)+
              (ey - oy)*(ey - oy));
}             

int Sensor::posIsAreaClear(double position, double width, double distance) 
{
  int i = 0;

  for(i = (int)(position - width/2); 
      i < (int)(position + width/2); 
      i++) 
  {
    if (m_daReadings[posWrap((int)position)] > -1)
      if (m_daReadings[posWrap((int)position)] < distance)
	return false;
  }
  return true;
}

void Sensor :: GetReading(double **arr, int histlen)
{
  for(int i = ZERO; i < histlen; i++) 
    memcpy(arr+(m_lSensorCount * i), Hist+(m_lSensorCount * i), m_lSensorCount);
}

void Sensor :: GetReading(double *arr)
{
  for (int i=0;i<m_lSensorCount;i++) {
    arr[i] = m_daReadings[i];
  }
}

double Sensor :: posGetAngle(int position)
{
  int pos = posWrap(position, m_lSensorCount);
  return m_daAngles[pos];
}

double Sensor :: posGetReading(int position, int histlen = 0)
{
  double ttl = 0.0;
  int cnt = 0;
  int pos = posWrap(position, m_lSensorCount);
  if (histlen <= 0) {
    return m_daReadings[pos];
  } else {
    // calculate average
    for (int i = m_lSensorHistCount + MAXHISTLEN - histlen; 
	 i < m_lSensorHistCount + MAXHISTLEN; i++) {
      if (i >= 0 && Hist[i % MAXHISTLEN][pos] != 0.0) {
	ttl += Hist[i % MAXHISTLEN][pos];
	cnt++;
      }
    }
    /*
    printf("hist[%d][%d]     = %f\n", (int)m_lSensorHistCount, pos, 
	   Hist[m_lSensorHistCount][pos]);
    */
    if (cnt) {
      // printf("ave hist         = %f\n", ttl / (double) cnt);
      return ttl / (double) cnt;
    } else {
      return -1.0; // no valid readings
    }
  }
}

double Sensor :: posGetReadingXCoord(int position)
{
  return m_daReadingsXCoord[posWrap(position, m_lSensorCount)];
}

double Sensor :: posGetReadingYCoord(int position)
{
  return m_daReadingsYCoord[posWrap(position, m_lSensorCount)];
}

double Sensor :: polGetReading(double dCoord)
  // dCoord is a polar angle, starting at zero (front) and going
  // around counter clockwise, to 2 PI.  DSB
{
  return degGetReading(P2D(dCoord));
}

double Sensor :: degGetReading(double dAngle)
  // dAngle is a degree, starting at zero (front) and going
  // around counter clockwise, to 360.  DSB
{
  double position;
  double delta1, delta2;
  int pos1, pos2;

  //Update(*m_dpOffset ); // will just return if no new data

  // FIX this is slightly wrong: pos 0 is not at angle 0
  // but slightly to the left (as you look at robot)

  position = (degWrap(dAngle) / 360.0) * m_lSensorCount;  
  // get position based on number of Sensor. Assumes even distribution

  pos1 = (int) position; // truncate
  pos2 = (pos1 + 1) % m_lSensorCount;       // next position higher

  if (position == ((double) pos1)) { // exactly at a sensor
    return m_daReadings[ pos1 ];
  } 

  // If either is a bad value, return the other
  // if both are bad, this will return -1

  if (m_daReadings[ pos1 ] == NEGONE)
    return m_daReadings[ pos2 ];
  if (m_daReadings[ pos2 ] == NEGONE)
    return m_daReadings[ pos1 ];

  // else, need to interpolate two surrounding positions:

  delta1 = 1.0 - (position - ((double) pos1)); // pos1 is smaller
  delta2 = 1.0 - delta1; // pos2 is greater

  return ((m_daReadings[ pos1 ] * delta1) + 
	  (m_daReadings[ pos2 ] * delta2));
}

void Sensor::UpdateReadings(void){
  Update( *m_dpOffset); // set m_dareadings[], etc.
}

double Sensor :: degGetReadingWindow(double dAngle, double dWindow )
  // dAngle is a degree, starting at zero (front) and going
  // around counter clockwise, to 360.  dWindow is a window
  // centered around dAngle, in degrees. DSB
{
  double dCurrentAngle;
  double dResolution;
  double dTotal;
  double dTotalDistance;
  double dDistance;
  double temp;
  
  //Update( *m_dpOffset);
  
  // a sensor every so many degrees:
  dResolution = (360.0 / m_lSensorCount);

  dTotal = 0.0;
  dTotalDistance = 0.0;

  for (dCurrentAngle = dAngle - (dWindow/2.0);  // might be negative
       dCurrentAngle < dAngle + (dWindow/2.0);  
       dCurrentAngle = (dResolution + dCurrentAngle)) {
    dDistance = (dWindow/2.0) - fabs(dAngle-dCurrentAngle);
    temp = degGetReading( degWrap(dCurrentAngle) );
    if (temp > NEGONE) {
      dTotal += temp * dDistance;
      dTotalDistance += dDistance;
    }
  }
  if (dTotalDistance > 0)
    return (dTotal/dTotalDistance);
  else return NEGONE;
}

double Sensor :: degGetMinAngle(void)
{
  return P2D(polGetMin().t);
}

double Sensor :: GetMinDist(void)
{
  return polGetMin().r;
}   

double Sensor :: degGetMaxAngle(void)
{
  return P2D(polGetMax().t);
}

double Sensor :: GetMaxDist(void)
{
  return polGetMax().r;
} 

Polar Sensor :: polGetMin(void)
{
  /*--- Local Declarations ---*/
  double mymin  = (double)100,
         myth   = (double)FZERO,
         tpos   = (double)FZERO,
         *array = NULL,
         radius = (double)FZERO;

  int minpos    = (int)ZERO,
      i         = (int)ZERO,
      pos       = (int)ZERO; 
 
  array = new double[m_lSensorCount];

  /*--- Execution ---*/

  for(pos=ZERO;pos<m_lSensorCount;pos++)
  {
    radius = array[pos] = posGetReading(pos);
    
    // -1 signifies a bad value for sonar
    if ( radius == -1 )
      continue;

    tpos = (PI)*2*(((double)pos)/((double)m_lSensorCount));
    radius = array[pos];

    // Make sure it is a valid reading
    if( finite(radius) && (radius < mymin ) )
    {
      mymin  = radius;
      myth   = tpos;
      minpos = pos;
    }
  }

  delete[] array;

  // This myth is relative to the front of robot!!! 0 to 2 pi
  // counter-clockwise DSB (only for B21R, SimBot)
  if (mymin == (double) 100) { // MAXIMUM
    return Polar(-1, -1);
  } else {
    return Polar(myth, mymin);
  }
}

Polar Sensor :: polGetMax()
{
  /*--- Local Declarations ---*/
  double mymax  = (double)NEGONE,
         myth   = (double)FZERO,
         tpos   = (double)FZERO,
         *array = NULL,
         radius = (double)FZERO;

  int maxpos    = ZERO,
      i         = ZERO,
      pos       = ZERO;

  array = new double[m_lSensorCount];

  for(pos=ZERO;pos<m_lSensorCount;pos++)
  {
    radius = array[pos] = posGetReading(pos);

    // -1 signifies a bad value for sonar
    if ( radius == -1 )
      continue;

    tpos = (PI)*2*(((double)pos)/((double)m_lSensorCount));

    //Check for valid reading
    if (finite(radius) && (radius > mymax ))
    {
      mymax  = radius;
      myth   = tpos;
      maxpos = pos;
    }
  }

  delete[] array;
  // This myth is relative to the front of robot!!! 0 to 2 pi
  // counter-clockwise DSB (only for B21R, SimBot)

  if (mymax == (double) -1) { // MINIMUM
    return Polar(-1, -1);
  } else {
    return Polar(myth, mymax);
  }
}

