#include "b21r.h"
#include "B21R.h"

b21r::b21r(int argc=0, char **argv=NULL) {
  //  dev = new B21R(argc, argv);
}

void b21r :: SensorsInit(void) {
}

void b21r :: UpdateReadings(void) {
}

double b21r :: degWrap(double dAngle) {
  return 0.0;
}

double b21r :: P2D(double dCoord) {
  return 0.0;
}

double b21r :: D2P(double dAngle) {
  return 0.0;
}

double b21r :: polWrap(double dCoord) {
  return 0.0;
}

void b21r :: setBrake(bool var) {
}

void b21r :: Localize(double var1, double var2 ,double var3) {
}

int b21r :: RobotControlModuleInit(void) {
  return 0;
}

int b21r :: UpdatePosition(void) {
  return 0;
}

int b21r :: SetVelos (double var1, double var2) {
  return 0;
}

void b21r :: Disconnect (void) {
}


