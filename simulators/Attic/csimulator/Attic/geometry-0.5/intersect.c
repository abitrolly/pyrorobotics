#include<assert.h>
#include<math.h>
#include"vops.h"

int isectLineSeg2d(float* sp0, float* sp1,
		 float* lp0, float* lp1, 
		 //returns (ignoring if NULL)
		 float* timeOfIntersection,
		 float* distanceToIntersection,
		 float* pointOfIntersection
		 ){
  assert(0);
  return 0;
}

int isectSegSeg2d(float* s0p0,float* s0p1,
		float* s1p0, float* s1p1,
		//returns (ignoring if NULL)
		float* timeOfIntersection,
		float* distanceToIntersection,
		float* pointOfIntersection
		){
  assert(0);
  return 0;
}
  
int isectRayPlane3d(float* location,float* direction,
		  float* plane, 
		  //returns (ignoring if NULL)
		  float* timeOfIntersection,
		  float* distanceToIntersection,
		  float* pointOfIntersection
		  ){
  assert(0);
  return 0;
}

int isectSegPlane3d(float* sp0, float* sp1, 
		  float* plane, 
		  //returns (ignoring if NULL)
		  float* timeOfIntersection,
		  float* distanceToIntersection,
		  float* pointOfIntersection
		  ){
  assert(0);
  return 0;
}

  int pointInTriangle(float* plane,
		      float* tp0,float* tp1,float* tp2){
    assert(0);
    return 0;
  }

  
int isectRayTri3d(float* location,float* direction, 
		float* tp0, float* tp1, float* tp2,
		//returns (ignoring if NULL)
		float* timeOfIntersection,
		float* distanceToIntersection,
		float* pointOfIntersection
		){
  float side0[3],side1[3];
  float plane[4],point[3];
  int result;
  
  vsub3d(tp2,tp0,side0);
  vsub3d(tp2,tp1,side1);
  
  vcross3d(side0,side1,plane);
  plane[3] = vdot3d(plane,tp0);

  result =
  isectRayPlane3d(location,direction,
		  plane,
		  timeOfIntersection,
		  distanceToIntersection,
		  point);

  result = result && pointInTriangle(point,tp0,tp1,tp2);

  if(pointOfIntersection)
    vcpy3d(point,pointOfIntersection);
  
  return result;
  }
  

int isectSegTri3d(float* sp0,float* sp1,
		float* tp0, float* tp1,float* tp2,
		//returns (ignoring if NULL)
		float* timeOfIntersection,
		float* distanceToIntersection,
		float* pointOfIntersection
		){
  float distance,length;
  float direction[3];
  int result;


  vsub3d(sp1,sp0,direction);
  length = sqrt(vdot3d(direction,direction));
  
  result = 
  isectRayTri3d(sp0,direction,
		tp0,tp1,tp2,
		timeOfIntersection,
		&distance,
		pointOfIntersection);

  result = result && (distance < length);

  if(distanceToIntersection)
    *distanceToIntersection = distance;

  return result;
}
  
