#include"intersect.h"
#include"vector.h"
#include"volume.h"
#include"compare.h"

int intersectSegSeg(float* A0, float* A1, 
		    float* B0, float* B1, 
		    float* D)
        {
        if(intersectLineSeg(A0,A1,B0,B1,D) 
	   && intersectLineSeg(B0,B1,A0,A1,D))
                return 1;

        return 0;
        }

int intersectLineSeg(float* L0, float* L1, 
		     float* S0, float* S1,
		     float* D)
        {
        float nL[2],dS[2],dLS[2],nd,t;


        if((S0[0] == S1[0]) && (S0[1] == S1[1])) //we only test real lines
                return 0;

        if((L0[0] == L1[0]) && (L0[1] == L1[1])) 
                return 0;

        nL[0] = -(L1[1] - L0[1]);  nL[1] = (L1[0] - L0[0]);   
        dS[0] =  (S1[0] - S0[0]);  dS[1] = (S1[1] - S0[1]); 

        nd = -dot(2,nL,dS);

        if(toleq(nd,0))
                return 0;

        dLS[0] = S0[0] - L0[0];
        dLS[1] = S0[1] - L0[1];

        t = dot(2,nL,dLS) / nd;

        if(t < 0)
                return 0;

        if(t > 1)
                return 0;

        D[0] = t*dS[0] + S0[0];
        D[1] = t*dS[1] + S0[1];

        return 1;
        }




int intersectRayPlane(float base[DIM],
		      float dir[DIM], 
		      float plane[DIM], 
		      float isect[DIM],
		      float t[0]){
  float d,n;
  int i;
  
  d = dot(DIM,plane,dir);

  if(d == 0) 
    return 0;

  n = plane[DIM] - dot(DIM,plane,base);
 
  *t = n/d;

  for(i=0; i<DIM; i++)
    isect[i] = base[i] + dir[i] * *t;

  return 1;
}

int intersectRayTri(float base[DIM],float dir[DIM], 
			 float pta[DIM], float ptb[DIM], float ptc[DIM],
			 float isect[DIM],float dist[0]){
  float plane[DIM+1];
  float volumes[3];
  int i;

  cross3D(pta,ptb,plane);
  plane[3] = dot(DIM,plane,pta);

  i = intersectRayPlane(base,dir,plane,isect,dist);

  if(i==0) 
    return 0;
  
  volumes[0] = volumeTetrahedron3d(base,isect,pta,ptb);
  volumes[1] = volumeTetrahedron3d(base,isect,ptb,ptc);
  volumes[2] = volumeTetrahedron3d(base,isect,ptc,pta);

  if(((volumes[0] >= 0) && (volumes[1] >= 0) && (volumes[2] >= 0)) ||
     ((volumes[0] <= 0) && (volumes[1] <= 0) && (volumes[2] <= 0))
     ) return 1;

  return 0;
}

int intersectSegPlane(float pta[DIM], 
			  float ptb[DIM], 
			  float plane[DIM+1], 
			  float isect[DIM]){
  float ray[DIM];
  int i;
  float dist;

  for(i=0; i<DIM; i++)
    ray[i] = pta[i] - ptb[i];
  
  i = intersectRayPlane(ptb,ray,plane,isect,&dist);

  if((i) && (dist >= 0) && (dist <= 1))
    return 1;
  return 0;
}

int intersectSegTri(float pta[DIM], float ptb[DIM],
			     float tpta[DIM],float tptb[DIM],float tptc[DIM],
			     float isect[DIM]){
  float ray[DIM];
  int i;
  float dist;
  
  for(i=0; i<DIM; i++)
    ray[i] = pta[i] - ptb[i];
  
  i = intersectRayTri(ptb,ray,tpta,tptb,tptc,isect,&dist);

  if((i) && (dist >= 0) && (dist <= 1))
    return 1;
  return 0;
}


