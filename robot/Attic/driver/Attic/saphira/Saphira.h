#ifndef  _SAPHIRA_H_
 #define _SAPHIRA_H_

class SFData {
 public:
  double x;
  double y;
  double z;
  double range;
  int flag;
};

class Saphira {
public:
  Saphira();
  ~Saphira( void );

  double _getSonarRange(int pos);
  double _getSonarXCoord(int num);
  double _getSonarYCoord(int num);
  double getSonarRange(int pos);
  double getSonarXCoord(int num);
  double getSonarYCoord(int num);
  SFData *SonarData;

  double getX(void);
  double getY(void);
  double getZ(void);
  double getTh(void);
  double getThr(void);

  int Disconnect( void );
  int Connect(int sim_robot);
  int Move(double translate_velocity, double rotate_velocity);
  int Rotate(double rotate_velocity);
  int Translate(double translate_velocity);
  int IsStall(void);
  int UpdatePosition(void);
  void UpdateReading(int num);
  void UpdateReadings(void);
  void Localize(double x, double y, double th);
  int getSonarCount(void);
  void setSonarFlag(int pos, int val);
  int getSonarFlag(int num);

  // Sensor locations and direction:
  double sonar_th (int pos);
  double sonar_x (int pos);
  double sonar_y (int pos);
  char * getType(void);

 private:
  double px;
  double py;
  double pz;
  double pth;
  double pthr;
  int SonarCount;
};

// ----------------------------------------

class CameraMover {
 private:
  int TiltAngle;
  int PanAngle;
  int ZoomAmount;  

 public:
  CameraMover ();
  ~CameraMover ();

  int getPanAngle(void);
  int getTiltAngle(void);
  int getZoomAmount(void);

  void Init();
  void Pan(int);
  void Tilt(int);
  void PanTilt(int, int);
  void Zoom(int);
  void Center();
};

#endif
