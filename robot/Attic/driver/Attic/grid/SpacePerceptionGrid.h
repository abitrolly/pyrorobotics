
#ifndef __SpacePerceptionGrid_h__
#define __SpacePerceptionGrid_h__


class SpacePerceptionGrid{
  float* data; //positive means hard
  float** grid;
  int width,height;
  int lowerBound,upperBound;
  float overshoot;
 public:
  SpacePerceptionGrid(int w,int h,int low, int high, float overshoot);
  ~SpacePerceptionGrid();
  void update(float xsrc, float ysrc, 
	      float xdst, float ydst, 
	      float angle, float delta,int hit);
  void decay(float dec);
  void reset();
  void recenter(int x, int y);
  float** getref();
  void copyregion(float** a, float** b, int x, int y, int w, int h);
  float get(int x,int y);
  //protected:
  void updateGridPoint(int x, int y, float delta);
  void updateGridRow(int y, int xmin, int xmax, float delta);  
  void updateGridLine(float* p0, float* p1, float delta);
  void updateGridTriangle(float* p0,float* p1,float* p2,float delta);
};

#endif

