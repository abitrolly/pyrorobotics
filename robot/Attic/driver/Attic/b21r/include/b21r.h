#ifndef  _B21RTOP_H_
 #define _B21RTOP_H_

class B21R;

class b21r
{
  public:

    /*--- Constructor ---*/
    b21r(int argc=0, char **argv=0);

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
    void Disconnect(void);
    
 private:
    B21R   *dev;

};

#endif
