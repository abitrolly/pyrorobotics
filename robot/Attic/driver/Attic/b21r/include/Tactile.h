#ifndef __SONAR_H__
 #define __SONAR_H__

/*--- PreProcessing Commands ---*/
#include <mobilitygeometry_i.h>
#include <mobilityutil.h>
#include "Vector.h"
#include "simple_templates.h"
#include "Sensor.h"

 #include <pthread.h>

/*--------------- CLASS SONAR SENSOR ----------------*/
class Tactile : public Sensor
{
 public:
    MobilityGeometry::PointState_var pTactilePoint;
    MobilityGeometry::Point3Data_var pTactileDat;

    static const int HISTLEN;
    static const double MAXSEGLEN;

    /*--- Sonar Methods --*/
    Tactile( void ) : Sensor() { }
    Tactile( double * dpOffset ) : Sensor(dpOffset) { }

    // Default str points to Enclosure Sonar
    void Init( mbyClientHelper *pHelper, char *RobotName, char *str );
    void Update(double);

    /*--- Mobility Specific Methods ---*/
    MobilityGeometry::PointState_var getpoint();

    MobilityGeometry::Point3Data_var getdat();
    /*--- Protected Area ---*/
 protected:
    
    /*--- Private Area ---*/
 private:


	pthread_mutex_t UpdateMutex;

	long lLastSample;
};

#endif


