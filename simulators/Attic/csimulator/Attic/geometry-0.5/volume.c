#include<assert.h>
#include<stdio.h>
#include"volume.h"

#define m3(i) ((i)%3)

float volumeTetrahedron(float* pta,float* ptb,float* ptc,float* ptd){
  float tpa[3];
  float tpb[3];
  float tpc[3];
  int i;
  
  for(i=0; i<3; i++){
    tpa[i] = pta[i] - ptd[i];
    tpb[i] = ptb[i] - ptd[i];
    tpc[i] = ptc[i] - ptd[i];
   }

  return (tpa[0] * (tpb[1]*tpc[2] - tpc[1]*tpb[2])
        -tpa[1] * (tpb[0]*tpc[2] - tpc[0]*tpb[2])
        +tpa[2] * (tpb[0]*tpc[1] - tpc[0]*tpb[1]))/6;
}
