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

PyObject *b21r :: getSonarHigh(void) {
  // return Python List
  PyObject *list = PyList_New(dev->HighSonar.m_lSensorCount);
  PyObject *element;
  for( int i=0; i< dev->HighSonar.m_lSensorCount; i++ ) {
    element = Py_BuildValue("f", dev->HighSonar.get(i));
    PyList_SET_ITEM( list, i, element);
  }
  return list;
}

PyObject *b21r :: getSonarLow(void) {
  // return Python List
  PyObject *list = PyList_New(dev->LowSonar.m_lSensorCount);
  PyObject *element;
  for( int i=0; i< dev->LowSonar.m_lSensorCount; i++ ) {
    element = Py_BuildValue("f", dev->LowSonar.get(i));
    PyList_SET_ITEM( list, i, element);
  }
  return list;
}

#define max(a,b) (((a)>(b))?(a):(b))

PyObject *b21r :: getLaser(void) {
  // return Python List
  PyObject *list = PyList_New(dev->MidLaser.m_lSensorCount);
  PyObject *element;
  for( int i=0; i< dev->MidLaser.m_lSensorCount; i++ ) {
    // Subtract the diameter of the robot, so distance is from 
    // robot's surface
    element = Py_BuildValue("f", max(dev->MidLaser.get(i) - 0.33, 0.0));
    PyList_SET_ITEM( list, i, element);
  }
  return list;
}

int b21r :: move(double translate, double rotate) {
  return (dev->SetVelos(translate, rotate));
}

double b21r :: getX() {
  return dev->getActualX();
}

double b21r :: getY() {
  return dev->getActualY();
}

double b21r :: getTh() {
  return dev->getActualDegth();
}

double b21r :: getThr() {
  return dev->getActualRadth();
}
