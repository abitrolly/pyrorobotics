#ifdef __cplusplus
extern "C"{
#endif

#define DIM 3

// A vector is DIM floats
// A plane is is a DIM vector plus a constant (distance from origin)


int intersectSegRay(float* pta,float* ptb,
			float* base,float* dir,
			float* isect,
			float* dist);

int intersectLineSeg(float* L0, float* L1, 
		     float* S0, float* S1,
		     float* D);

int intersectSegSeg(float* pta,float* ptb,
		    float* ptc, float* ptd,
		    float* isect);

int intersectSegmentPlane(float* pta, float* ptb, 
			  float* plane, 
			  float* isect);

int intersectRayPlane(float* base,float* dir,
		      float* plane, 
		      float* isect,float* dist);

int intersectRayTriangle(float* base,float* dir, 
			 float* pta, float* ptb, float* ptc,
			 float* isect,float* dist);

int intersectSegmentTriangle(float* base,float* dir,
			     float* pta,float*ptb,float* ptc,
			     float* isect);



#ifdef __cplusplus
}
#endif
