#include "Sonar.h"
#include <pthread.h>

double const Sonar::MAXSEGLEN = 5.0;

void Sonar::Init( mbyClientHelper *pHelper, char *RobotName, char *str )
{
  CORBA::Object_ptr                  ptempObj;
  char pathName[255];

  sprintf(pathName, str, RobotName);
  ptempObj = pHelper->find_object(pathName);

  try
    {
      pSonarSeg = MobilityGeometry::SegmentState::_narrow(ptempObj);
    }

  catch (...)
    {
      fprintf(stderr,"\nSonar failed to start. Aborting.\n");
      throw;
    }

  pSonarDat = pSonarSeg->get_sample(ZERO);
  
  /* setup sensor history variables */
  m_lSensorCount = pSonarDat->org.length();
  SensorCount = m_lSensorCount>0 ? m_lSensorCount: 24;
  m_daReadings.SetSize(m_lSensorCount);
  m_daReadingsXCoord.SetSize(m_lSensorCount);
  m_daReadingsYCoord.SetSize(m_lSensorCount);

  Hist = new double*[MAXHISTLEN];
  for( int i=0; i < MAXHISTLEN; i++)
    Hist[i] = new double[MAXHISTLEN];

  m_daAngles = new double [m_lSensorCount];
  for (int i = 0;i < m_lSensorCount;i++) {
    m_daAngles[i] = (i * 15) + 7.5;
  }

  printf("Sonar initialized\n");
  pthread_mutex_init(&UpdateMutex,NULL);
  lLastSample = 0;
}

void Sonar :: Update( double dOffset )
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
  pSonarDat = pSonarSeg->get_sample(ZERO);

  if (lLastSample == pSonarDat->timestamp.SampleID) {
	  pthread_mutex_unlock(&UpdateMutex);
	  return;
  }
  
  lLastSample = pSonarDat->timestamp.SampleID;

  for (i = 0;i < m_lSensorCount;i++) {
    seglength = seglen(pSonarDat->org[i].x,
		       pSonarDat->org[i].y,
		       pSonarDat->end[i].x,
		       pSonarDat->end[i].y);

    m_daReadings[(lOffset+i)%m_lSensorCount] = seglength;
    m_daReadingsXCoord[(lOffset+i)%m_lSensorCount] = pSonarDat->end[i].x;
    m_daReadingsYCoord[(lOffset+i)%m_lSensorCount] = pSonarDat->end[i].y;
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


