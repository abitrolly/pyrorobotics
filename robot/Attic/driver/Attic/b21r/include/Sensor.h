#include "Robot.h"
#include "Vector.h"
#include "simple_templates.h"

#ifndef __SENSOR_H__
 #define __SENSOR_H__

typedef struct
{
   unsigned long SampleID;

   double        Reading;

} SensorData;

class Sensor
{
 public:
    /*--- General Constant Definitions ---*/
    static const float FZERO;
    static const double DZERO;
    static const int   ZERO;
    static const int   NEGONE;
    static const int   MAXHISTLEN;

    Robot *m_pRobot;
    double height;

    /*
       dOffset is always in radians
    */
    virtual void Update( double dOffset ) = 0;
    void UpdateReadings(void);
    double seglen( double ox, double oy, double ex, double ey );
    int posWrap( int iPos, int SensorCount = 24);
    double P2D (double dCoord);
    double degWrap( double dAngle );

    Sensor( void ) { 
      m_lSensorHistCount = 0;
      m_dpOffset = (double *)&DZERO;
    }

    Sensor( double * dpOffset ) { 
      m_lSensorHistCount = 0;
      m_dpOffset = dpOffset; 
    }
    
    virtual ~Sensor() {}

    virtual int    posIsAreaClear(double position, double width, double distance);
    virtual void   GetReading(double **arr, int histlen);
    virtual void   GetReading(double *arr);
    virtual double posGetAngle(int position);
    virtual double posGetReading(int position, int histlen = 0);
    virtual double posGetReadingXCoord(int position);
    virtual double posGetReadingYCoord(int position);
    virtual double polGetReading(double dCoord);
    virtual double degGetReading(double dAngle);
    virtual double degGetReadingWindow(double dAngle, double dWindow );
    virtual double degGetMinAngle(void);
    virtual double GetMinDist(void);
    virtual double degGetMaxAngle(void);
    virtual double GetMaxDist(void);
    virtual Polar  polGetMin(void);
    virtual Polar  polGetMax();
    double get(int pos);
    double * m_dpOffset;
    long SensorCount;    
    long m_lSensorCount;    

 protected:
    long m_lSensorHistCount;
    double *m_daAngles; // angles of sonars

    unsigned long lLastSample;
    pthread_mutex_t UpdateMutex; 

    //    TCArray< TCQueue< SensorData, SensorData & >,
    //             TCQueue< SensorData, SensorData & > > m_aHistory;
    TCArray< double, double & > m_daReadings;
    TCArray< double, double & > m_daReadingsXCoord;
    TCArray< double, double & > m_daReadingsYCoord;
    double **Hist;

 private:

};

#endif
