#ifndef  _B21R_H_
 #define _B21R_H_

# include "mobility.h"
# include "Constants.h"
# include "Robot.h"
# include "Sonar.h"
# include "Laser.h"

//#include "Tactile.h"
//#include "Infrared.h"
//#include "speech.h"  //generic speech file

#include "B21RCamMover.h"

/****************************************************
  B21R Class
***************************************************/
class B21R : public Robot 
{
  public:

    /*--- Constructor ---*/
    B21R(int argc=ZERO, char **argv=NULL);

    /*--- Virtual Functions in Robot class ---*/
    void   SensorsInit           (void);
    void   UpdateReadings        (void);

    double degWrap( double dAngle );
    double P2D (double dCoord);
    double D2P (double dAngle);
    double polWrap( double dCoord );
    void   setBrake              (bool);
    void   Localize              (double,double,double);

    int    RobotControlModuleInit(void); 
    int    UpdatePosition        (void);
    int    SetVelos              (double,double);

    Polar  polGetMin             (void);
    Polar  polGetMax             (void);

    double degGetMinAngle        (void);
    double degGetMaxAngle        (void);
    double GetMinDist         (void);
    double GetMaxDist         (void);
    double getPower              (void);
    void Disconnect(void);

    /*--- Public Variables ---*/

    // Mobility objects here
    CORBA::Object_ptr ptempObj;
    mbyClientHelper   *pHelper;

    MobilityCore    ::ObjectDescriptor_var  pDescriptor;
    MobilityActuator::ActuatorState_var     pDriveCommand;
    MobilityActuator::ActuatorData          OurCommand;
    MobilityActuator::ActuatorState_var     pOdoState;
    MobilityActuator::ActuatorData          pOdoData;
    MobilityActuator::ActuatorState_var     pSkirtState;
    MobilityActuator::ActuatorData          pSkirtData;
      
    double SkirtPose;

    char PathName[PATHNAME];

    // Sensor Systems
    Sonar   HighSonar;
    Sonar   LowSonar;
    Laser   MidLaser;

    double offset_x;
    double offset_y;
    double offset_t;

//    IR      Ir;                               // Infrared
//    Tactile HighTact;                         // Enclosure Tactile
//    Tactile LowTact;                          // Base Tactile
};

#endif
