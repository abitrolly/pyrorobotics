#ifndef  _ROBOT_H_
 #define _ROBOT_H_

class Point;
class Segment;
class xcPosition;

#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <stdio.h>
#include "Vector.h"
#include "Constants.h"
#include "simple_templates.h"
#include "pthread.h"
//#include "CamMover.h"

class Robot 
{
 public:
  //CamMover *CameraMover;

  static const int    SPEED;
  static const int    TURN;
  static const int    TRANSLATE;
  static const int    ROTATE;
  static const int    MAXSPEED;
  static const int    FLIGHT_HISTORY;
  
  static const int    X;
  static const int    Y;
  static const int    THETA;
  
  static const float  MINDIST; 
  static const float  R2D;
  static const float  D2R;
  
  static const double MAXVAL;
  static const double MINVAL;
  
  /*--- Public Variables ---*/
  int   Debug_Level;
  const double &x,
    &y,
    &degth,
    &radth;
  
  double       cur_translate,
    cur_rotate;
  
  int          argc;
  char         **argv;
  
  bool         xcMANUAL;
  int          xcStall;
  double       turn_request;
  double       speed_request;
  
  int RUN_SKIRTPOSE;
  
  /*----- Variables/Fuctions for the Robot Network Server ------*/
  int port_number, port_min, port_max, hosts_count;
  char hosts[30][128];
  pthread_t server_thread;
  char robot_id[256];
  int socket;
  //void StartNetworkServer();
  //void StopNetworkServer();
  
  char         *robot_type;
  /*--- Constructor / Destructor ---*/
  Robot(int,char**);
  virtual ~Robot() {FlightHistory.RemoveAll();}
  
  /*--- Robot Methods ---*/
  virtual int RobotControlModuleInit(void)=0;
  
  virtual int SetVelos         (double translate_velocity,
				double rotate_velocity)=0;
  
  virtual int UpdatePosition   ()=0;
  virtual void UpdateReadings  (void)=0;
  
  double xcDistance(double,double); 
  double xcDistance(double,double,double,double);
  double xcToAngle(double phi);
  double xcToAngle(double phi, double theta);
  double xcAngle   (double,double); 
  double xcAngle   (double,double,double,double,double);
  
  virtual void SensorsInit     (void)=0;
  virtual void Localize        (double x, double y, double th)=0;
  virtual void Reset() { Localize(0, 0, 0); }
  virtual Polar polGetMin      ()=0;
  virtual Polar polGetMax      ()=0;
  
  virtual double degGetMinAngle()=0;
  virtual double degGetMaxAngle()=0;
  virtual double GetMinDist ()=0;
  virtual double GetMaxDist ()=0;
  virtual double degGetReading(double) {return 0;}    
  
  virtual double getPower()=0;
  virtual void Disconnect()=0;
  
  virtual double getActualX();
  virtual double getActualY();
  virtual double getActualRadth();
  virtual double getActualDegth();
  
  int setRobotPosition(double, double, double);
  int setRobotPositionR(double, double, double);
  int setRobotPositionD(double, double, double);
  int setX(double);
  int setY(double);
  int setDegth(double);
  int setRadth(double);
  
  double checkRegion(int iMinMax,char * szRegion, int iUnionIntersect= xcINTERSECTION);
  double occupyRegion(int iMinMax,double lfX1,double lfY1,double lfX2,double lfY2);
  
  //Flight History Stuff
  void   AddPoint              (Point*);
  Point  *GetHistoryReading    (int);
  
  // Get Functions for protected/private area;
  char *getRobotName(void);
  int   getRobotID  (void);
  void Say(char *fmt, ...);

  char *replchar(char *buff, char c, char n);
  bool file_exist(char *filename);
  double P2D (double dCoord);
  double degWrap( double dAngle );
  
  /*--- Protected Area ---*/
 protected:
  char *RobotName;         // Robot Name
  
  int  RobotID;            // Robot ID
  
  double px,               // Current X-Coordinate
    py,               // Current Y-Coordinate
    degpth,           // Current Theta Rotation Degrees
    radpth;           // Current Theta Rotation Radians
  
  Vector Min,
    Max;
  
  TCList<Point*,Point*> FlightHistory;
};	

class Point 
{
  public:    double x;
    double y;
    double z;
    double degth;
    double radth;

    Point(double mx    =(double)FZERO,
          double my    =(double)FZERO,
          double mdegth=(double)FZERO,
          double mradth=(double)FZERO,
          double mz=(double)FZERO)
    {
       x = mx;
       y = my;
       degth = mdegth;
       radth = mradth;
       z = mz;
    }
};

class Segment {
 public: 
  Point *org;
  Point *end;
  double z1;
  double z2;
  Segment *next;
};

class xcPosition {
 public:
  double x;
  double y;
  double radTh;
  xcPosition(void) { 
    x = 0;
    y = 0;
    radTh = 0;
  }
  xcPosition(double x1, double y1, double rth) { 
    x = x1;
    y = y1;
    radTh = rth;
  }
  xcPosition(Point p, double rth) { 
    x = p.x;
    y = p.y;
    radTh = rth;
  }
  /*
    xcPosition(Point *p, double rth) { 
    x = p->x;
    y = p->y;
    radTh = rth;
  }
  */
};


#endif



