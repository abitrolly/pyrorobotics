#include "b21r.h"
#include "B21R.h"

b21r::b21r(int argc=0, char **argv=NULL) {
  dev = new B21R(argc, argv);
}

void b21r :: initSkirtPose(void) {
  dev->initSkirtPose();
}

void b21r :: SensorsInit(void) {
  dev->SensorsInit();
}

void b21r :: UpdateReadings(void) {
  dev->UpdateReadings();
}

double b21r :: degWrap(double dAngle) {
  return dev->degWrap(dAngle);
}

double b21r :: P2D(double dCoord) {
  return dev->P2D(dCoord);
}

double b21r :: D2P(double dAngle) {
  return dev->D2P(dAngle);
}

double b21r :: polWrap(double dCoord) {
  return dev->polWrap(dCoord);
}

void b21r :: setBrake(bool var) {
  dev->setBrake(var);
}

void b21r :: Localize(double var1, double var2 ,double var3) {
  dev->Localize(var1, var2, var3);
}

int b21r :: RobotControlModuleInit(void) {
  return dev->RobotControlModuleInit();
}

int b21r :: UpdatePosition(void) {
  return dev->UpdatePosition();
}

int b21r :: SetVelos (double var1, double var2) {
  return dev->SetVelos(var1, var2);
}

void b21r :: Disconnect (void) {
  dev->Disconnect();
}


