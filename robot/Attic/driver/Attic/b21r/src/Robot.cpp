#include "Robot.h"
#include <signal.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>

const int Robot::SPEED          = 0;
const int Robot::TURN           = 1;
const int Robot::TRANSLATE      = 0;
const int Robot::ROTATE         = 1;
const int Robot::MAXSPEED       = 1;
const int Robot::FLIGHT_HISTORY = 500;
const int Robot::X              = 1;
const int Robot::Y              = 0;
const int Robot::THETA          = 2;

const float  Robot::MINDIST = 30.0; // 30cm
const float  Robot::R2D     = ((float)180.0 / (float)PI);
const float  Robot::D2R     = ((float)PI    / (float)180.0);

const double Robot::MAXVAL  = (double)99999.0;
const double Robot::MINVAL  = (double)0.0;

//void *Child(void * object);
//void *Listen(void * object);

//extern void *Child(void *);
//extern void *Listen(void *);

Robot :: Robot(int argnum, char **argstr) : x(px), 
                                            y(py),
                                            degth(degpth),
                                            radth(radpth),
                                            xcMANUAL(false)
{
  Point p(x,y,degth,radth);
 
  argc          = argnum;
  argv          = argstr;

  //CameraMover   = NULL;
  cur_translate = ZERO;
  cur_rotate    = ZERO;
  xcStall       = 0;
  turn_request  = 0;
  speed_request = 0;

  Debug_Level = 10; // atoi(xrcl::get_option(argc, argv, "-debug", "0"));
  RobotName = "B21R"; // xrcl::get_option(argc, argv, "-robot");
  RobotID   = ZERO;

  if(RobotName == NULL)
  {
    fprintf(stderr,"\nNeed a robot name to use.\n");
    exit(NEGONE);
  }

  FlightHistory.AddHead(&p);

  char buf[256]; 
  sprintf(buf,"%s/bin/network.conf",getenv("XRCL_HOME"));
  FILE *fis = fopen(buf,"r");
  if (fis == NULL) {
    perror("Couldn't open network.conf");
    exit(1);
  }
  fscanf(fis,"%d %d",&port_min,&port_max);
  hosts_count = 0;
  while( 1 == fscanf (fis,"%s",hosts[hosts_count])) hosts_count++;
  strcpy(robot_id,"");
  fclose(fis);
  //if (strcmp(xrcl::get_option(argc, argv, "-hb", "off"), "off") != 0) {
  //  HB = new HandyBoard(xrcl::get_option(argc, argv, "-hb", "off"));
  //}
}

double Robot::P2D (double dCoord) 
  // Polar to Degrees
  // Slow, but let's double check everything before we 
  // optimize. DSB
{
  return degWrap((dCoord / PI) * 180.0);
}

double Robot::degWrap( double dAngle )
  // Degree wrap-around
{
  double temp=(double) (((int) dAngle) % ((int)360) + (dAngle - (int) dAngle));
  while (temp < 0)
    temp += 360;
  return temp;
}

void Robot::AddPoint(Point *p)
{
  if(FlightHistory.GetCount() >= FLIGHT_HISTORY)
     FlightHistory.RemoveTail();

  FlightHistory.AddHead(p);
}

bool Robot::file_exist(char *filename) {
  FILE *fp;
  if ((fp = fopen(filename, "r")) != NULL) {
    int err = fclose(fp);
    if (err != 0) {
      perror("FATAL ERROR: closing file");
      exit(1);
    }
    return true;
  }
  return false;
}

char *Robot::replchar(char *buff, char c, char n) {
  static char buffer[512];
  int j = 0;
  for (unsigned int i = 0; i < strlen(buff) + 1; i++, j++) {
    if (buff[i] == c) {
      buffer[j] = n;
    } else {
      buffer[j] = buff[i];
    }
  }
  return buffer;
}

Point* Robot::GetHistoryReading(int index=ZERO)
{
   POSITION pos    = NULL;

   Point    *pNext = NULL;

   int      count  = ZERO;

   if(index < ZERO || index > FLIGHT_HISTORY)
      return(FlightHistory.GetAt(FlightHistory.GetHeadPosition()));
   
   pos = FlightHistory.GetHeadPosition();
   while(pos)
   {
      pNext = FlightHistory.GetAt(pos);

      if(count == index)
         return(pNext);
      else
      {
         FlightHistory.GetNext(pos);
         count++;
      }
  } //End while

  return(NULL);
}

int Robot::getRobotID(void)
{
  /*--- Execution ---*/
  return(RobotID);
}

char *Robot::getRobotName(void)
{
  /*--- Execution ---*/
  return(RobotName);
}

double Robot :: xcDistance(double x1, double y1)
{
  return(xcDistance(x1,y1,x,y)); 
}

double Robot :: xcDistance(double x1, double y1,
                              double x2, double y2) 
{
  /*--- Local Declarations ---*/
  Polar p;

  /*--- Execution ---*/
  p.SetCartesian(x1 - x2, y1 - y2); // range pi to -pi
  return(p.r);
}

double Robot :: xcToAngle(double phi) {
  // Given an angle in degrees (0 front, to left to 360), what is the
  // shortest way to turn there?  returns -180 to 180, neg to right,
  // to use with turning
  return xcToAngle(phi, degth);
}

double Robot :: xcToAngle(double phi, double theta) {
  if(phi > theta) // turn left
  {
    phi = phi - theta;
  } 
  else // turn right
  {
    phi = (theta - phi) * -1;
  }
  
  if (phi > 180) // oops, shorter to turn other direction
    {
      phi = (360 - phi) * -1;
    }
  
  if (phi < -180) // oops, shorter to turn other direction
    {
      phi = (360 + phi);
    }                        
  return phi;
}

double Robot :: xcAngle(double x1, double y1, 
                           double x2, double y2, double theta)
{
  /*--- Local Declarations ---*/
  Polar  p;
  double phi = (double)FZERO; 
  int    dir = ZERO;

  /*--- Execution ---*/
  p.SetCartesian(x1 - x2, y1 - y2); // range pi to -pi

  if(p.t < ZERO) 
     phi = p.t + 2 * PI; // 0 to pi to left; 0 to -pi to right
  else
    phi = p.t;

  phi = P2D(phi);

  return xcToAngle(phi, theta);
}

double Robot :: xcAngle(double x1, double y1)
{
  return xcAngle(x1,y1,x,y,degth);
}

double Robot :: checkRegion(int iMinMax,char * szRegion, int iUnionIntersect)
{
  int i,iCountRegions=0,iCountUnique=0;
  int iRegionsToCheck[8]={-1,-1,-1,-1,-1,-1,-1,-1};
  int iNumToCheck=0;
  int iRegions[3][4];

  double lfAngle;
  double lfReadings[10];
  double lfRegionValue[8];
  double lfStartingAngles[8]={ 22.5,
			       -22.5,
			       -67.5,
			       -112.5,
			       -157.5,
			       157.5,
			       112.5,
			       67.5};
  double lfCheckValue;

  //                   |       |
  //            lf  0  | f 1   |  rf 2
  //            _______|_______|_______
  //                   |       |
  //            l  7   |       |  r  3
  //            _______|_______|_______
  //                   |       |
  //            lb  6  | b 5   |  br 4
  //                   |       |


  //Parse szRegion to determine which sides requested and set flags accordingly

  //Each "direction" identifies three regions to check
  //These are stored temporarily in the iRegions array
  //For example if 'F' is specified we have {0,1,2}
  //If 'L' is also specified we have {0,6,7}
  //IF "LF" is to mean we want only to search in {0}
  //Then we are interested in the intersection
  //If we would like for it to mean {0,1,2,6,7}
  //Then we are interested in the union
  //This file uses conditional compilation to select the method
  //Comment out the method you don't want or remove it completely
 
  //The distances found will be radial distances
  //Having the distance from a plane on each side of the robot may be more useful
  //This modifiaction can be made very easily using trigonometry

  for(i=0;i<strlen(szRegion);i++)
    {
      switch(szRegion[i])
	{
	case 'L':
	case 'l':   iRegions[0][iCountRegions]=0;
		    iRegions[1][iCountRegions]=6;
		    iRegions[2][iCountRegions++]=7;
	            break;
	case 'R':
	case 'r':   iRegions[0][iCountRegions]=2;
		    iRegions[1][iCountRegions]=3;
		    iRegions[2][iCountRegions++]=4;
	            break;
	case 'F':
	case 'f':   iRegions[0][iCountRegions]=0;
		    iRegions[1][iCountRegions]=1;
		    iRegions[2][iCountRegions++]=2;
	            break;
	case 'B':
	case 'b':   iRegions[0][iCountRegions]=4;
		    iRegions[1][iCountRegions]=5;
		    iRegions[2][iCountRegions++]=6;
	            break;

	}
    }

  if (xcUNION == iUnionIntersect) 
    {
      //Take the union of all region sets
      for(i=0;i<iCountRegions;i++)
	{
	  for(int k=0;k<3;k++)
	    {
	      int fUnique=true;
	      for(int j=0;j<8;j++)  
		{ 

		  if(iRegions[k][i]==iRegionsToCheck[j])
		    fUnique=false;
		}
	      if(fUnique)
		{
		  iRegionsToCheck[iNumToCheck++]=iRegions[k][i];
		}
	    }
	}

    } 
  else if (xcINTERSECTION == iUnionIntersect) 
    {
      //Take the intersection of all region sets
      for(i=0;i<3;i++)
	{
	  int iCandidate=iRegions[i][0];
	  int fOverlap=true;

	  for(int j=1;j<iCountRegions;j++)
	    {
	      int fMatch=false;

	      for(int k=0;k<3;k++)
		{	      
		  if(iRegions[k][j]==iCandidate)
		    fMatch=true;
		}

	      fOverlap&=fMatch;
	    }
	  if(fOverlap)
	    {
	      iRegionsToCheck[iNumToCheck++]=iCandidate;
	    }
	}
    }

  // Now have region(s) to check so start checking them

  if(iMinMax==xcMAX)  lfCheckValue=0.0;
  if(iMinMax==xcMIN)  lfCheckValue=1000.0;
 
  //For each region to check
  for(i=0;i<iNumToCheck;i++)
    {
      //Initialize test value to something small for MAX,something big for MIN
      if(iMinMax==xcMAX)  lfRegionValue[i]=0.0;
      if(iMinMax==xcMIN)  lfRegionValue[i]=1000.0;

      //This takes 10 Readings in each region at 4.5 degrees separation
      for(int j=0;j<10;j++)
	{
	  lfAngle=lfStartingAngles[(iRegionsToCheck[i])]+4.5*j;

	  // Replace my degGetReading with the call to proper function
	  lfReadings[j]=degGetReading(lfAngle);

	  if(iMinMax==xcMAX)
	    {
	      if(lfReadings[j]>lfRegionValue[i])
		lfRegionValue[i]=lfReadings[j];
	    }
	  if(iMinMax==xcMIN)
	    {
	      if(lfReadings[j]<lfRegionValue[i])
		lfRegionValue[i]=lfReadings[j];
	    }
	}

      if(iMinMax==xcMAX)
	{
	  if(lfRegionValue[i]>lfCheckValue)
	    lfCheckValue=lfRegionValue[i];
	}
      if(iMinMax==xcMIN)
	{
	  if(lfRegionValue[i]<lfCheckValue)
	    lfCheckValue=lfRegionValue[i];
	}
    }

  return lfCheckValue;
}

double Robot :: occupyRegion(int iMinMax,double lfX1,double lfY1,double lfX2,double lfY2)
{
  double lfSweepAngle,lfRadSweepAngle,lfAngleStep=5.0;
  double lfReading,lfOccupancyValue;
  double lfReadingX,lfReadingY;
  double lfTempX,lfTempY;

   //   Robot Heading is along the Y axis
  //
  //                    ^ Y
  //                    |
  //                    |
  //           X <--------------
  //                    |
  //                    |

  // I tried to come up with a way to sweep only those areas
  // Which might be in the box but never came up with anything
  // That would always work.  This function currently sweeps
  // through 360 degrees at intervals of 5 degrees and then checks
  // To see if the reading is in the box.  If you can
  // come up with something bettter -- change it.


  //Want x1,y1 to specify lower left corner
  if(lfX1>lfX2)
    {
      lfTempX=lfX1;
      lfX1=lfX2;
      lfX2=lfTempX;
    }

  if(lfY1>lfY2)
    {
      lfTempY=lfY1;
      lfY1=lfY2;
      lfY2=lfTempY;
    }
 
  if(iMinMax==xcMAX) lfOccupancyValue=-1.0;
  if(iMinMax==xcMIN) lfOccupancyValue=1000.0;

  for(lfSweepAngle=0.0;lfSweepAngle<360.0;lfSweepAngle+=lfAngleStep)
    {
      // Replace my degGetReading with the right function call
      lfReading=degGetReading((lfSweepAngle>180.0)? lfSweepAngle - 360.0 : lfSweepAngle);
      
      lfRadSweepAngle=(lfSweepAngle*3.14159)/180.0;

      lfReadingX=lfReading * sin(lfRadSweepAngle);
      lfReadingY=lfReading * cos(lfRadSweepAngle);

      // If Reading is in specified rectangle
      if((lfReadingX >=lfX1) && (lfReadingX <=lfX2) && (lfReadingY >=lfY1) && (lfReadingY <=lfY2))
	{
	
	  if((iMinMax==xcMAX) && (lfReading>lfOccupancyValue)) lfOccupancyValue=lfReading;
	  if((iMinMax==xcMIN) && (lfReading<lfOccupancyValue)) lfOccupancyValue=lfReading;
	}
    }
  return ((lfOccupancyValue==1000.0) ? -1.0: lfOccupancyValue);
}

/*
void Robot::StartNetworkServer()
{
  pthread_create(&server_thread, NULL, &Listen, this);
}
void Robot::StopNetworkServer()
{
  pthread_cancel(server_thread);
  shutdown(socket,2);
}

*/


double Robot::getActualX() {
  return x;
}

double Robot::getActualY() {
  return y;
}

double Robot::getActualRadth() {
  return radth;
}

double Robot::getActualDegth() {
  return degth;
}

/// set robot position
int Robot::setRobotPosition(double _x, double _y, double _t) {
  setRobotPositionD(_x, _y, _t);

  return 0;
}

int Robot::setRobotPositionR(double _x, double _y, double _t) {
  px = _x;
  py = _y;
  radpth = _t;
  
  return 0;
}

int Robot::setRobotPositionD(double _x, double _y, double _t) {
  px = _x;
  py = _y;
  degpth = _t;
  
  return 0;
}

int Robot::setX(double _x) {
  px = _x;
  
  return 0;
}

int Robot::setY(double _y) {
  py = _y;

  return 0;
}

int Robot::setDegth(double _degth) {
  degpth = _degth;
  // set radpth
  radpth = (degpth / 180) * M_PI;

  return 0;
}

int Robot::setRadth(double _radth) {
  radpth = _radth;

  // set degpth
  degpth = (degpth * 180) / M_PI;

  return 0;
}

void Robot::Say(char *fmt, ...) {
  va_list     ap;
  void        *data[20];
  static char command[512];
  static char buffer[512];
  static char phrasefile[512];
  char *newbuf;
  int         i = ZERO;
  //time_t time_start, time_stop;
  struct stat fileinfo;
  
  va_start(ap, fmt);
  for(i=ZERO;i<20;i++) 
  {
     data[i] = va_arg(ap, void *);
  }
  va_end(ap);

  sprintf(buffer, fmt, 
	   data[ 0], data[ 1], data[ 2], data[ 3], data[ 4],
	   data[ 5], data[ 6], data[ 7], data[ 8], data[ 9], 
	   data[10], data[11], data[12], data[13], data[14], 
	   data[15], data[16], data[17], data[18], data[19]);
  /* Old Version
  sprintf(command, "echo \"%s\" | /usr/lib/festival/bin/festival_client --async --ttw --aucommand 'na_play $FILE'", buffer);
  */

  newbuf = replchar(buffer, '.', ';');
  sprintf(phrasefile, "/tmp/%s.au", newbuf);

  if (! file_exist(phrasefile)) {
    sprintf(command, "echo \"%s\" | /usr/lib/festival/bin/festival_client --async --ttw > \"/tmp/%s.au\"",
	    newbuf,
	    newbuf );
    system(command);
  }
  system("aumix -m 0 -v 100");
  sprintf( command, "na_play \"%s\"",
	   phrasefile );
  stat(phrasefile, &fileinfo);
  //if (HB) {
  //  fprintf(stderr, "handy board!\n");
  //  HB->talk(fileinfo.st_size / 33000);
  //} 
  system( command );
}
