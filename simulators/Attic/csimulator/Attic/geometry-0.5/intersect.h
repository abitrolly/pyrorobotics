#ifndef __INTERSECT_H__
#define __INTERSECT_H__

#ifdef __cplusplus
extern "C" {
#endif

  //This code is all 3 dimentional
 
  int isectLineSeg2d(float* sp0, float* sp1,
		   float* lp0, float* lp1, 
		   //returns (ignoring if NULL)
		   float* timeOfIntersection,
		   float* distanceToIntersection,
		   float* pointOfIntersection
		   );

  int isectSegSeg2d(float* s0p0,float* s0p1,
		  float* s1p0, float* s1p1,
		  //returns (ignoring if NULL)
		  float* timeOfIntersection,
		  float* distanceToIntersection,
		  float* pointOfIntersection
		  );
  
  int isectRayPlane3d(float* location,float* direction,
		    float* plane, 
		    //returns (ignoring if NULL)
		    float* timeOfIntersection,
		    float* distanceToIntersection,
		    float* pointOfIntersection
		    );

  int isectSegPlane3d(float* sp0, float* sp1, 
		    float* plane, 
		    //returns (ignoring if NULL)
		    float* timeOfIntersection,
		    float* distanceToIntersection,
		    float* pointOfIntersection
		    );
  
  int pointInTriangle(float* plane,
		      float* tp0,float* tp1,float* tp2);

  int isectRayTri3d(float* location,float* direction, 
		  float* tp0, float* tp1, float* tp2,
		  //returns (ignoring if NULL)
		  float* timeOfIntersection,
		  float* distanceToIntersection,
		  float* pointOfIntersection
		  );
  
  int isectSegTri3d(float* location,float* direction,
		  float* tp0, float* tp1,float* tp2,
		  //returns (ignoring if NULL)
		  float* timeOfIntersection,
		  float* distanceToIntersection,
		  float* pointOfIntersection
		  );
  

#ifdef __cplusplus
}
#endif

#endif
