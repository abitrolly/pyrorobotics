#include "Laser.h"
#include <pthread.h>

double const Laser::MAXSEGLEN = 15.0;

void Laser::Init( mbyClientHelper *pHelper, char *RobotName, char *str )
{
  CORBA::Object_ptr                  ptempObj;
  char pathName[255];

  sprintf(pathName, str, "Pls");
  ptempObj = pHelper->find_object(pathName);

  try
    {
      pLaserSeg = MobilityGeometry::SegmentState::_narrow(ptempObj);
    }

  catch (...)
    {
      fprintf(stderr,"\nLaser failed to start. Aborting.\n");
      throw;
    }

  pLaserDat = pLaserSeg->get_sample(ZERO);
  
  /* setup sensor history variables */
  m_lSensorCount = pLaserDat->org.length();
  m_daReadings.SetSize(m_lSensorCount);

  Hist = new double*[MAXHISTLEN];
  for( int i=0; i < MAXHISTLEN; i++)
    Hist[i] = new double[MAXHISTLEN];
  
  m_daAngles = new double [m_lSensorCount];
  for (int i = 0;i < 180;i++) {
    if (i < 90)
      m_daAngles[i] = 90 - i + 270;
    else
      m_daAngles[i] = i - 90;
  }

  printf("Laser initialized\n");
  pthread_mutex_init(&UpdateMutex,NULL);
  lLastSample = 0;
}

void Laser :: Update( double dOffset )
{
  double       r = (double)FZERO;
  int i = ZERO;
  SensorData Data, Compare;
  bool bNewReading;
  double dReading, seglength, *valid_reading;

  valid_reading = new double[m_lSensorCount];
  
  /*--- Execution ---*/
  long lOffset = (long)(dOffset / (2*PI) * m_lSensorCount);
  pthread_mutex_lock(&UpdateMutex);
  pLaserDat = pLaserSeg->get_sample(ZERO);

  // RWI BUG! 
  // appears that timestamp.SampleID is always 0   -DSB

  if ((pLaserDat->timestamp.SampleID != 0) && 
      lLastSample == pLaserDat->timestamp.SampleID) {
    // fprintf(stderr, "returning because %d == %d\n", lLastSample, 
    // pLaserDat->timestamp.SampleID);
    pthread_mutex_unlock(&UpdateMutex);
    return;
  } else { fprintf( stderr, "L" ); }
  

  lLastSample = pLaserDat->timestamp.SampleID;

  for (i = 0;i < m_lSensorCount;i++) {
    seglength = seglen(pLaserDat->org[i].x,
		       pLaserDat->org[i].y,
		       pLaserDat->end[i].x,
		       pLaserDat->end[i].y);

    m_daReadings[(lOffset+i)%m_lSensorCount] = seglength;
  }

  m_lSensorHistCount = ++m_lSensorHistCount % MAXHISTLEN;
  for( i=0; i< m_lSensorCount; i++ ) {
    if ( m_daReadings[(lOffset+i)%m_lSensorCount] > MAXSEGLEN ||
	 m_daReadings[(lOffset+i)%m_lSensorCount] < 0.001 )
      {
	double left, right;
	if ( i == 0 )
	  left = m_daReadings[(lOffset+m_lSensorCount-1)%m_lSensorCount];
	else
	  left = m_daReadings[(lOffset+i-1)%m_lSensorCount];
	right = m_daReadings[(lOffset+i+1)%m_lSensorCount];
	m_daReadings[(lOffset+i)%m_lSensorCount] = (right + left)/2;
      }
    Data.Reading = m_daReadings[(lOffset+i)%m_lSensorCount];
    Hist[m_lSensorHistCount][(lOffset+i)%m_lSensorCount] = 
      m_daReadings[(lOffset+i)%m_lSensorCount];
  }
  pthread_mutex_unlock(&UpdateMutex);
}

double Laser :: degGetReading(double dAngle) {
  int pos;
  // take angle that is 0 in front, counter clockwise increasing
  // error if angle in back
  if (dAngle > 90 && dAngle < 270)
    return -1.0;
  if (dAngle >= 270)
    pos = (int)fabs(dAngle - 270);
  else 
    pos = (int)(dAngle - 90);
  // return pos that is 0 at robot's right, counter clockwise increasing
  return m_daReadings[ pos ];
}

