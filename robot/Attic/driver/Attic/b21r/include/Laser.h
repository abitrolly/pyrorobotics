#ifndef __Laser_H__
 #define __Laser_H__

/*--- PreProcessing Commands ---*/
#include <mobilitygeometry_i.h>
#include <mobilityutil.h>
#include "Vector.h"
#include "simple_templates.h"
#include "Robot.h"
#include "Sensor.h"

#include <pthread.h>

/*--------------- CLASS Laser SENSOR ----------------*/
class Laser : public Sensor
{
 public:
    MobilityGeometry::SegmentState_var pLaserSeg;
    MobilityGeometry::SegmentData_var  pLaserDat;

    static const int HISTLEN;
    static const double MAXSEGLEN;

    /*--- Laser Methods --*/
    Laser( void ) : Sensor() { 
      m_dpOffset =  (double *)&DZERO; 
    }
    Laser( double * dpOffset ) : Sensor(dpOffset) { }

    // Default str points to Enclosure Laser
    void Init( mbyClientHelper *pHelper, char *RobotName, char *str );
    void Update( double dOffset );
    double degGetReading(double dAngle);
    /*--- Mobility Specific Methods ---*/
    MobilityGeometry::SegmentState_var getseg() 
    	{ Update(*m_dpOffset); return pLaserSeg; }
    MobilityGeometry::SegmentData_var  getdat() 
    	{ Update(*m_dpOffset); return pLaserDat; }

    /*--- Protected Area ---*/
 protected:
    
    /*--- Private Area ---*/
 private:


	pthread_mutex_t UpdateMutex;

	unsigned long lLastSample;
};

#endif


