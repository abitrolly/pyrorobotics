
#include<math.h>
#include<limits.h>
#include<stddef.h>
#include"intersect.h"

//this is not very triangle specific. The code is optimized for
//least effort in programming. There exists information that
//could complexify the logic but simplify the calculation. 
//(except for data structure size i am not using the knowledge
//that i am converting a triangle (the algo is much more general than
//triangles)
void scanConvertTriangle(float* p0, float* p1, float* p2,
			 void (*horizontalLine)(int,int,int)){
  float* pts[3];
  float miny = INT_MAX; //(surely this is big enough?)
  float maxy = INT_MIN;
  int x[2];
  int y,ic,i;
  float isect[2] ;
  float la[2] = {INT_MAX,0},lb[2] = {INT_MIN,0};
  float t;

  pts[0] = p0; pts[1] = p1; pts[2] = p2;

  for(i=0; i<3; i++){
    if(pts[i][1] < miny) 
      miny = floor(pts[i][1]);
    if(pts[i][1] > maxy) 
      maxy = ceil(pts[i][1]);
    if(pts[i][0] < la[0])
      la[0] = pts[i][0];
    if(pts[i][0] > lb[0])
      lb[0] = pts[i][0];
  }
  for(y=miny; y<=maxy; y++){
    la[1] = lb[1] = y;
    for(i=0,ic=0; (i<3) && (ic<2); i++)
      if(isectLineSeg2d(la,lb,pts[i],pts[(i+1)%3],NULL,NULL,isect))
	x[ic++] = isect[0];
    if(x[0] > x[1]){
      t = x[0]; x[0] = x[1]; x[1] = t;
    }
    x[0] = ceil(x[0]);
    x[1] = floor(x[1]);
    horizontalLine(y,(int)x[0],(int)x[1]);
  }
}

