#include "Tactile.h"
#include "Constants.h"
#include <pthread.h>

double const Tactile::MAXSEGLEN = 15;

/*-------------- Class Tactile Constructor ------------------*/
void Tactile::Init( mbyClientHelper *pHelper, char *RobotName, char *str )
{
 /*--- Mobility Overhead ---*/
  CORBA::Object_ptr                  ptempObj;
  char pathName[255];

  /*--- Execution ---*/
  sprintf(pathName, str, RobotName);
  ptempObj = pHelper->find_object(pathName);

  try
    {
      pTactilePoint = MobilityGeometry::PointState::_narrow(ptempObj);
    }

  catch (...)
    {
      fprintf(stderr,"\nTactile failed to start. Aborting.\n");
      throw;
    }

  pTactileDat = pTactilePoint->get_sample(ZERO);
  
  /* setup sensor history variables */
  m_lSensorCount = pTactileDat->point.length();
  m_daReadings.SetSize(m_lSensorCount);

  Hist = new double*[MAXHISTLEN];
  for( int i=0; i < MAXHISTLEN; i++)
    Hist[i] = new double[MAXHISTLEN];

  fprintf(stderr,"-------------Tactile inintialized\n");
  
  pthread_mutex_init(&UpdateMutex,NULL);

  lLastSample = -1;

}

MobilityGeometry::PointState_var Tactile::getpoint()
{
  Update(0.0); // FIX: bottom of B21R has offset (I think) -DSB
  return pTactilePoint;
}

MobilityGeometry::Point3Data_var Tactile::getdat() 
{
  Update(0.0); // FIX: bottom of B21R has offset (I think) -DSB
  return pTactileDat;
}

void Tactile :: Update(double dOffset)
{
  double       r = (double)FZERO;
 
  int i = ZERO;
 
  SensorData Data, Compare;
  bool bNewReading;
  double dReading, seglength;
  long lOffset = (long)(dOffset / (2*PI) * m_lSensorCount); 
  /*--- Execution ---*/
 
  pTactileDat = pTactilePoint->get_sample(ZERO);
 
  /* if no new data then just quit */
 
  if (lLastSample == pTactileDat->timestamp.SampleID) {
	  pthread_mutex_unlock(&UpdateMutex);
	  return;
  }
  
  lLastSample = pTactileDat->timestamp.SampleID;

  m_lSensorHistCount = ++m_lSensorHistCount % MAXHISTLEN;
  for (i = 0;i < m_lSensorCount;i++) {
    m_daReadings[(lOffset+i)%m_lSensorCount] = pTactileDat->point[i].flags;
    Hist[m_lSensorHistCount][(lOffset+i)%m_lSensorCount] = 
      m_daReadings[(lOffset+i)%m_lSensorCount];
  }
  pthread_mutex_unlock(&UpdateMutex);
}

