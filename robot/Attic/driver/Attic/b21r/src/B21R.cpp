#include "B21R.h"


/**********************************************************
 Robot Classes: B21R
 **********************************************************/

B21R :: B21R(int argc, char **argv) : Robot(argc, argv)
{
  RUN_SKIRTPOSE = 1;
  //if (strcmp(xrcl::get_option(argc, argv, "-cameras", "off"), "on") == 0) {
  //  CameraMover = new B21RCamMover();
  //}
  offset_x = 0.0;
  offset_y = 0.0;
  offset_t = 0.0;
  Localize((double)FZERO,(double)FZERO,(double)FZERO);
  RobotControlModuleInit();
  SensorsInit();
}

/*--------------- Class B21R RobotControlModuleInit -------------*/  
int B21R :: RobotControlModuleInit(void)
{
   /*--- Execution ---*/
   // All Mobility servers and clients use CORBA and this initialization
   // is required for the C++ language mapping of CORBA.

  px = ZERO;
  py = ZERO;
  degpth = ZERO;
  radpth = ZERO;

  pHelper = new mbyClientHelper(argc, argv);

  /*------------------ ROBOT DRIVE MODULE ----------------------*/
  // Build pathname to the component we want to use to drive the robot.
  // RobotName is loaded because of Robot constructor

  fprintf( stderr, "Attaching to \'%s/Drive/Command\' ...",
	   RobotName );
  sprintf(PathName, "%s/Drive/Command", RobotName);
  ptempObj = pHelper->find_object(PathName);
  try
    {
      pDriveCommand = MobilityActuator::ActuatorState::_duplicate(MobilityActuator::ActuatorState::_narrow(ptempObj));
    }
  catch (...)
    {
      return(NEGONE);
    }
  fprintf( stderr, "Done.\n" );
  
  // 2 axes of command 
  OurCommand.velocity.length(2);
  OurCommand.velocity[SPEED] = FZERO;
  OurCommand.velocity[TURN]  = FZERO;
  pDriveCommand->new_sample(OurCommand,ZERO);
  
  /*------------------ ODOMETER MODULE -----------------------*/
  fprintf( stderr, "Attaching to \'%s/Drive/State\' ...",
	   RobotName );
  sprintf(PathName, "%s/Drive/State", RobotName);
  ptempObj = pHelper->find_object(PathName);
  try
    {
      pOdoState = MobilityActuator::ActuatorState::_duplicate(MobilityActuator::ActuatorState::_narrow(ptempObj));
    }
  catch (...)
    {
      return(NEGONE);
    }
  fprintf( stderr, "Done\n" );

    /*------------------ SKIRTPOSE MODULE -----------------------*/

    fprintf( stderr, "Attaching to \'%s/SkirtPose\' ...\n",
	     RobotName );
    sprintf(PathName, "%s/SkirtPose", RobotName);
    ptempObj = pHelper->find_object(PathName);
    try
      {
	pSkirtState = MobilityActuator::ActuatorState::_duplicate(MobilityActuator::ActuatorState::_narrow(ptempObj));
      }
    catch (...) {
      return(NEGONE);
    }
    fprintf( stderr, "Done...\n" );

    fprintf( stderr, "RUN_SKIRTPOSE: %d\n",
	     RUN_SKIRTPOSE);

  if ( RUN_SKIRTPOSE ) {
    SkirtPose = 2 * PI;
    // Set initial postition of robot
    UpdatePosition();
    SetVelos(0,0.8);
    int counter = 0;
    while (SkirtPose > 0.2 || SkirtPose < 0.1) {
      UpdatePosition();
      if (counter % 68 == 0) {
	fprintf(stderr,"\n[Skirt %.2f]",SkirtPose);
      } else fprintf(stderr, ".");
      SetVelos(0,0.8);
      counter++;
    }
  }

    SetVelos(0,0.0);
    UpdatePosition();
  
  // Everything is OK!!
  fprintf( stderr, "OK.\n" );
  return(ZERO);
}

/*--------------- Class B21R SensorInit --------------------*/
void B21R :: SensorsInit(void) 
{
  /*--- Execution ---*/
  fprintf( stderr, "Attaching to \'%s/BaseSonar/Segment\' ...\n",
	   RobotName );
  LowSonar = Sonar(&SkirtPose); // reinit with offset
  LowSonar.Init   (pHelper, RobotName, "%s/BaseSonar/Segment" );
  LowSonar.m_pRobot = this;
  LowSonar.height = .11;
  
  fprintf( stderr, "Attaching to \'Pls/Laser/Segment\' ...\n" );
  MidLaser.Init( pHelper, RobotName, "%s/Laser/Segment"       );
  MidLaser.m_pRobot = this;
  MidLaser.height = 0.38;

  fprintf( stderr, "Attaching to \'%s/Sonar/Segment\' ...\n",
	   RobotName );
  HighSonar.Init  (pHelper, RobotName, "%s/Sonar/Segment"     );  
  HighSonar.m_pRobot = this;
  HighSonar.height = .74;

  //if (strcmp(xrcl::get_option(argc, argv, "-cameras", "off"), "on") == 0) {
  //  CameraMover->Init();
  //}
}

//  Ir.Init         (argc, argv, RobotName, pHelper);
//  TopTact.Init    (argc, argv, RobotName, pHelper, 
//                   "%s/EnclosureContact/Point");
//  BtmTact.Init    (argc, argv, RobotName, pHelper);


template <class T> T min(T x,T y) { if (x < y) return x;return y; }

/*--------------- Class B21R UpdateReadings --------------------*/
void B21R :: UpdateReadings(void)
{
  /*--- Execution ---*/
  static double last_x, last_y, last_degth;
  HighSonar.UpdateReadings();
  MidLaser.UpdateReadings();
  LowSonar.UpdateReadings();
  xcStall = 0;
  // 0 - no stall
  // 1 - stall translate
  // 2 - stall rotate
  // 3 - both stalled
  if (speed_request > 0 && (last_x == x && last_y == y)) {
    xcStall += 1;
  }
  if (turn_request > 0 && (last_degth == degth)) {
    xcStall += 2;
  }
  last_x = x;
  last_y = y;
  last_degth = degth;
}

double B21R :: degWrap( double dAngle )
  // Degree wrap-around
{
  double temp=(double) (((int) dAngle) % ((int)360) + (dAngle - (int) dAngle));
  while (temp < 0)
    temp += 360;
  return temp;
}

double B21R::P2D (double dCoord) 
  // Polar to Degrees
  // Slow, but let's double check everything before we 
  // optimize. DSB
{
  return degWrap((dCoord / PI) * 180.0);
}

double B21R::D2P (double dAngle) 
  // Degrees to Polar
  // Slow, but let's double check everything before we 
  // optimize. DSB
{
  return polWrap((dAngle / 180.0) * PI);
}

double B21R::polWrap( double dCoord )
  // Polar coordinate wrap-around
{
  return (P2D(dCoord) / 180.0) * PI;
}

/*-------------- Class B21R UpdatePosition -----------------*/
int B21R :: UpdatePosition(void)
{
  /*--- Execution ---*/
  pOdoState->update_sample(ZERO,pOdoData);
  px     = -((double)pOdoData.position[X]) - offset_x;
  py     = ((double)pOdoData.position[Y]) - offset_y;

  degpth = (double)degWrap((((pOdoData.position[THETA]+PI) / 
			     (2 * PI)) * 360) - 90 - offset_t);
  radpth = D2P(degth);

  if(Debug_Level > ONE)
     fprintf(stderr,"\nB21R LOCATION: X: %f\tY: %f\tDegTH: %f\tRadTH: %f\n",
                    (float)x,(float)y,(float)degth,(float)radth);

  pSkirtState->update_sample(ZERO,pSkirtData);
  SkirtPose = pSkirtData.position[ZERO];
  if(SkirtPose < ZERO)
    SkirtPose = (2*PI) + SkirtPose;

  // Update Flight Recorder
  // pref_flight_recorder
  if (0) {
    Point p(x,y,degth,radth);
    AddPoint(&p);
  }

  // Everything is OK!!
  return(ZERO);
}

/*------------ B21R SetVelos Function -----------------*/
int B21R :: SetVelos(double translate_velocity, double rotate_velocity)
{
  // rotate    = - turns to right, + turns to left
  // translate = - goes back, + goes forward

  int tran_dir;
  if (translate_velocity - cur_translate > 0) 
    tran_dir = 1;
  else 
    tran_dir = -1;

  int rot_dir;
  if (rotate_velocity - cur_rotate > 0) 
    rot_dir = 1;
  else 
    rot_dir = -1;

  /*--- Execution ---*/
  if (fabs(translate_velocity - cur_translate) > 0.1) {
    translate_velocity = tran_dir * 0.1 + cur_translate;
  }
  if (fabs(rotate_velocity - cur_rotate) > 0.1) {
    rotate_velocity = rot_dir * 0.1 + cur_rotate;
  }

  if(translate_velocity > 1)
    translate_velocity = 1;

  if(rotate_velocity > 1)
    rotate_velocity = 1;

  if(translate_velocity < -1)
    translate_velocity = -1;

  if(rotate_velocity < -1)
    rotate_velocity = -1;

  if (translate_velocity < 0 && cur_translate > 0)
    translate_velocity = 0;
  if (translate_velocity > 0 && cur_translate < 0)
    translate_velocity = 0;
  if (rotate_velocity < 0 && cur_rotate > 0)
    rotate_velocity = 0;
  if (rotate_velocity > 0 && cur_rotate < 0)
    rotate_velocity = 0;

  OurCommand.velocity[SPEED] = translate_velocity;
  OurCommand.velocity[TURN]  = rotate_velocity;

  // This is what we are telling it, not actual!
  // FIX
  cur_translate = translate_velocity;
  cur_rotate    = rotate_velocity;

  pDriveCommand->new_sample(OurCommand,ZERO);

  // Everything is OK!!
  return(ZERO);
}

void B21R :: Localize(double x, double y, double th)
{
  offset_x = px - x;
  offset_y = py - y;
  offset_t = degpth - th;
}

/*--------------- Class B21R polGetMax --------------------*/
Polar B21R :: polGetMax(void)
{
  /*--- Local Declarations ---*/
  Polar emax = HighSonar.polGetMax();
  Polar bmax = LowSonar.polGetMax();

  /*--- Execution ---*/
  if(emax.r == NEGONE)
    return(bmax);
  if(bmax.r == NEGONE)
    return(emax);
  if(emax.r > bmax.r)
    return(emax);
  else
   return(bmax);
}

/*--------------- Class B21R polGetMin --------------------*/
Polar B21R :: polGetMin(void)
{
  /*--- Local Declarations ---*/
  Polar emin = HighSonar.polGetMin();
  Polar bmin = LowSonar.polGetMin();
 
  /*--- Execution ---*/
  if(emin.r == NEGONE)
    return(bmin);
  if(bmin.r == NEGONE)
    return(emin);
  if(emin.r < bmin.r)
    return(emin);
  else
    return(bmin);
}

/*--------------- Class B21R degGetMinAngle --------------------*/
double B21R :: degGetMinAngle(void)
{
  /*--- Local Declarations ---*/
  double emin = HighSonar.degGetMinAngle();
  double bmin = LowSonar.degGetMinAngle();
  
  /*--- Execution ---*/
  if(emin == NEGONE)
    return(bmin);
  if(bmin == NEGONE)
    return(emin);
  if(emin < bmin)
    return(emin);
  else
    return(bmin);
}

/*--------------- Class B21R degGetMaxAngle --------------------*/
double B21R :: degGetMaxAngle(void)
{
  /*--- Local Declarations ---*/
  double emax = HighSonar.degGetMaxAngle();
  double bmax = LowSonar.degGetMaxAngle();
 
  /*--- Execution ---*/
  if(emax == NEGONE)
    return(bmax);
  if(bmax == NEGONE)
    return(emax);
  if(emax > bmax)
    return(emax);
  else
    return(bmax);
}

/*--------------- Class B21R getGetMinDist ----------------*/
double B21R :: GetMinDist(void)
{
  /*--- Local Declarations ---*/
  double emin = HighSonar.GetMinDist();
  double bmin = LowSonar.GetMinDist();

  /*--- Execution ---*/
  if(emin == NEGONE)
    return(bmin);
  if(bmin == NEGONE)
    return(emin);
  if(emin < bmin)
    return(emin);
  else
    return(bmin);
}

/*--------------- Class B21R GetMaxDist --------------------*/
double B21R :: GetMaxDist(void)
{
  /*--- Local Declarations ---*/
  double emax = HighSonar.GetMaxDist();
  double bmax = LowSonar.GetMaxDist();

  /*--- Execution ---*/
  if(emax == NEGONE)
    return(bmax);
  if(bmax == NEGONE)
    return(emax);
  if (emax > bmax)
    return(emax);
  else
    return(bmax);
}

/*--------------- Class B21R GetPower --------------------*/
double B21R :: getPower(void) 
{
  /*--- Execution ---*/
  return((double)ONE);
} 

void B21R :: Disconnect(void) {
  // Nothing to do for B21R ?
}

/*--------------- Class B21R setBrake --------------------*/
void B21R :: setBrake(bool value)
{
  //  if ( value )
    //on_general_command( "EnableMotion", NULL );
    //else
    //on_general_command( "DisableMotion", NULL );
}

