#include "Saphira.h"
#include <math.h>
#include "saphira.h" // ActivMedia's C header

const double PI = (double) M_PIl;
const double PIOVER180 = PI / 180.0;
const double DEG90RADS = 0.5 * PI;
const double COSDEG90RADS = cos(DEG90RADS) / 1000.0;
const double SINDEG90RADS = sin(DEG90RADS) / 1000.0;

extern "C" void myStartupFn(void) {
  sfSetDisplayState(sfGLOBAL, TRUE);	/* use the global view */
}
  
extern "C" void myConnectFn(void) {
  sfInitBasicProcs();		/* start up comm processes */
}

extern "C" void SaphiraInit(void) {
  sfOnConnectFn(myConnectFn);	/* register a connection function */
  sfOnStartupFn(myStartupFn);	/* register a startup function */
}

Saphira :: Saphira() {
}

Saphira :: ~Saphira( void ) {
  sfDisconnectFromRobot();
}

int Saphira :: Disconnect( void ) {
  sfDisconnectFromRobot();
  return 1;
}

double Saphira::getX(void) {
  return px;
}

double Saphira::getTh(void) {
  return pth;
}

double Saphira::getThr(void) {
  return pthr;
}

double Saphira::getY(void) {
  return py;
}

double Saphira::getZ(void) {
  return pz;
}

int Saphira :: Connect(int sim_robot = 1) {
  SaphiraInit(); 
  sfStartup(1);
  char *saphira_compipe = getenv("SAPHIRA_COMPIPE");
  if (sim_robot) { // simulator?
    if (saphira_compipe == NULL) {
      fprintf(stderr, "WARNING: SAPHIRA_COMPIPE not set in env; using /tmp/robot\n");
      saphira_compipe = "/tmp/robot";
    }
    sfConnectToRobot(sfLOCALPORT, saphira_compipe); /* simulator */
  } else 
    sfConnectToRobot(sfTTYPORT, sfCOM1); 
  int pausecnt = 0;
  while (!sfIsConnected && pausecnt++ < 10) {
    sfPause(100);
  }
  if (!sfIsConnected) {
    printf("Unable to connect!");
    return -1;
  }
  // init sonar readings:
  SonarCount = sonar_num;
  SonarData = new SFData[SonarCount];
  for (int i = 0;i < SonarCount;i++) {
    SonarData[i].z = 0.0;
  }
  // robot position:
  pz = 0.0;
  px = 0.0;
  py = 0.0;
  pth = 0.0;
  pthr = 0.0;
  return 1;
}

void Saphira :: UpdateReadings(void) {
  for (int i = 0;i < SonarCount;i++) {
    UpdateReading(i);
  }
  UpdatePosition();
}

void Saphira :: UpdateReading(int num) {
  if (sfSonarNew(num)) {
    SonarData[num].range = _getSonarRange(num);
    if (SonarData[num].range < 2.999) {
      SonarData[num].x = _getSonarXCoord(num);
      SonarData[num].y = _getSonarYCoord(num);
      SonarData[num].flag = 1; // new
    } else {
      SonarData[num].x = _getSonarXCoord(num); // ok, i think
      SonarData[num].y = _getSonarYCoord(num); // ok, i think
      SonarData[num].flag = 2; // out of range
    }
  } else {
    SonarData[num].flag = 0; // out of range
  }
}

void Saphira::setSonarFlag(int pos, int val) {
  SonarData[pos].flag = val;
}

int Saphira :: getSonarCount(void) { 
  return SonarCount;
}
double Saphira :: getSonarXCoord(int num) { 
  return SonarData[num].x;
}

double Saphira :: getSonarYCoord(int num) { 
  return SonarData[num].y;
}

int Saphira :: getSonarFlag(int num) { 
  int retval = SonarData[num].flag;
  SonarData[num].flag = 0; // After reading the flag, change it to old
  return retval;
}

double Saphira :: getSonarRange(int num) { 
  return SonarData[num].range;
}

double Saphira :: _getSonarXCoord(int num) { 
  /* returns X coord as float */
    return (double) (COSDEG90RADS * sfSonarXCoord(num) -
		     SINDEG90RADS * sfSonarYCoord(num));
}

double Saphira :: _getSonarYCoord(int num) { 
  /* returns hit Y coord as float */
  return (double) -(SINDEG90RADS * sfSonarXCoord(num) +
		    COSDEG90RADS * sfSonarYCoord(num));
}

double Saphira :: _getSonarRange(int pos) {
  /* sfSonarRange() returns an int */
  return (double) (sfSonarRange(pos) / 1000.0); 
}

int Saphira :: IsStall(void) {
  return sfStalledMotor(sfLEFT) + sfStalledMotor(sfRIGHT) * 2;
  // 0 - no stall
  // 1 - stall on left
  // 2 - stall on right
  // 3 - both stalled
}

int Saphira :: UpdatePosition(void) {
  px = sfRobot.ax / 1000.0;
  py = sfRobot.ay / 1000.0;
  pth = sfRobot.ath;
  pthr = pth * PIOVER180;
  return 1;
}

int Saphira :: Move(double translate_velocity, double rotate_velocity) {
  sfSetVelocity((int)(translate_velocity * 1100.0));
  sfSetRVelocity((int)(rotate_velocity * 75.0)); 
  return 1;
}

int Saphira :: Rotate(double rotate_velocity) {
  sfSetRVelocity((int)(rotate_velocity * 75.0)); 
  return 1;
}

int Saphira :: Translate(double translate_velocity) {
  sfSetVelocity((int)(translate_velocity * 1100.0));
  return 1;
}

// Change x, y, and th on robot
void Saphira :: Localize(double x, double y, double th) {
  sfRobot.ax = x * 1000.0;
  sfRobot.ay = y * 1000.0;
  sfRobot.ath = th; // degrees
}

double Saphira :: sonar_th (int pos) {
  double retval = 0.0;
  switch (pos) {
  case 0:
    retval = (double) 90.0; // degrees here, radians below
    break;
  case  (  1):
    retval = (double) 50.0;
    break;
  case  (  2):
    retval = (double) 30;
    break;
  case  (  3):
    retval = (double) 10;
    break;
  case  (  4):
    retval = (double) - 10;
    break;
  case  (  5):
    retval = (double) - 30;
    break;
  case  (  6):
    retval = (double) - 50;
    break;
  case  (  7):
    retval = (double) - 90;
    break;
  case  (  8):
    retval = (double) - 90;
    break;
  case  (  9):
    retval = (double) - 130;
    break;
  case  (  10):
    retval = (double) - 150;
    break;
  case  (  11):
    retval = (double) - 170;
    break;
  case  (  12):
    retval = (double) 170;
    break;
  case  (  13):
    retval = (double) 150;
    break;
  case  (  14):
    retval = (double) 130;
    break;
  case  (  15):
    retval = (double) 90;
    break;
  }
  return retval * PIOVER180; // return radians
}
    
double Saphira :: sonar_x (int pos) {
  switch(pos) {
  case (0):
    return (double)   .145;
  case  ( 1):
    return (double)   .185;
  case  ( 2):
    return (double)   .220;
  case  ( 3):
    return (double)   .240;
  case  ( 4):
    return (double)   .240;
  case  ( 5):
    return (double)   .220;
  case  ( 6):
    return (double)   .185;
  case  ( 7):
    return (double)   .145;
  case  ( 8):
    return (double)    -.145;
  case  ( 9):
    return (double)    -.185;
  case  ( 10):
    return (double)   -.220;
  case  ( 11):
    return (double)   -.240;
  case  ( 12):
    return (double)   -.240;
  case  ( 13):
    return (double)   -.220;
  case  ( 14):
    return (double)   -.185;
  case  ( 15):
    return (double)   -.145;
  }
  return (double) -1;
}

double Saphira :: sonar_y (int pos) {
  switch (pos) {
  case (0):
    return (double) (  .130);
  case  (1):
    return (double) (  .115);
  case  (2):
    return (double) (  .080);
  case  (3):
    return (double) (  .025);
  case  (4):
    return (double) (  -.025);
  case  (5):
    return (double) (  -.080);
  case  (6):
    return (double) (  -.115);
  case  (7):
    return (double) (  -.130);
  case  (8):
    return (double) (  -.130);
  case  (9):
    return (double) (  -.115);
  case  (10):
    return (double) (  -.080);
  case  (11):
    return (double) (  -.025);
  case  (12):
    return (double) (  .025);
  case  (13):
    return (double) (  .080);
  case  (14):
    return (double) (  .115);
  case  (15):
    return (double) (  .130);
  }
  return (double) -1;
}

// ------------------------------------------------
// CameraMover code
// ------------------------------------------------

extern "C" void sfPTZCamInit(void);
extern "C" void sfPTZCamPan(int);
extern "C" void sfPTZCamTilt(int);
extern "C" void sfPTZCamPanTilt(int, int);
extern "C" void sfPTZCamZoom(int);

CameraMover::CameraMover() {
  // constructor
  PanAngle = 0;
  TiltAngle = 0;
  ZoomAmount = 0;
}

CameraMover::~CameraMover() {
  // deconstruct
}

void CameraMover::Init() {
  fprintf(stderr, "Initializing PTZ unit...");
  sfPTZCamInit();
  usleep(1000 * 1000); // 1 second
  Center();
  fprintf(stderr, "...done!\n");
}

void CameraMover::Pan(int degrees) {
  PanAngle = degrees;
  sfPTZCamPan(degrees);
}

void CameraMover::Tilt(int degrees) {
  TiltAngle = degrees;
  sfPTZCamTilt(degrees);
}

void CameraMover::PanTilt(int pdegrees, int tdegrees) {
  TiltAngle = tdegrees;
  PanAngle = pdegrees;
  sfPTZCamPanTilt(pdegrees, tdegrees);
}

void CameraMover::Zoom(int amount) {
  ZoomAmount = amount;
  sfPTZCamZoom(amount);
}

void CameraMover::Center() {
  sfPTZCamPanTilt(0, 0);
  PanAngle = 0;
  TiltAngle = 0;
  ZoomAmount = 0;
}
