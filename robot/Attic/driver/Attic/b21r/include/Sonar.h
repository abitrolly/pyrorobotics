#ifndef __SONAR_H__
 #define __SONAR_H__

/*--- PreProcessing Commands ---*/
#include <mobilitygeometry_i.h>
#include <mobilityutil.h>
#include "Vector.h"
#include "simple_templates.h"
#include "Robot.h"
#include "Sensor.h"

 #include <pthread.h>

/*--------------- CLASS SONAR SENSOR ----------------*/
class Sonar : public Sensor
{
 public:
    MobilityGeometry::SegmentState_var pSonarSeg;
    MobilityGeometry::SegmentData_var  pSonarDat;

    static const double MAXSEGLEN;

    /*--- Sonar Methods --*/
    Sonar( void ) : Sensor() { 
      m_dpOffset =  (double *)&DZERO; 
    }
    Sonar( double * dpOffset ) : Sensor(dpOffset) { }

    // Default str points to Enclosure Sonar
    void Init( mbyClientHelper *pHelper, char *RobotName, char *str );
    void Update( double dOffset );

    /*--- Mobility Specific Methods ---*/
    MobilityGeometry::SegmentState_var getseg() 
    	{ Update(*m_dpOffset); return pSonarSeg; }
    MobilityGeometry::SegmentData_var  getdat() 
    	{ Update(*m_dpOffset); return pSonarDat; }

    /*--- Protected Area ---*/
 protected:
    
    /*--- Private Area ---*/
 private:


	pthread_mutex_t UpdateMutex;

	unsigned long lLastSample;
};

#endif


