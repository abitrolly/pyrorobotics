#include<math.h>

#include"compare.h"

#include"vops.h"

float E0[] = {1,0,0,0,0};
float E1[] = {0,1,0,0,0};
float E2[] = {0,0,1,0,0};
float E3[] = {0,0,0,1,0};
float E4[] = {0,0,0,0,1};

float* vcpy(int dim,float* a,float* d){
  for(dim--;dim >=0;dim--)
    d[dim] = a[dim];
  return d;
}

float* vadd(int dim,float* a, float* b, float* d){
  for(dim--;dim >=0;dim--)
    d[dim] = a[dim]+b[dim];
  return d;
}

float* vsub(int dim,float* a, float* b, float* d){
  for(dim--;dim >=0;dim--)
    d[dim] = a[dim]-b[dim];
  return d;
}

float* vmul(int dim,float* a, float* b, float* d){
  for(dim--;dim >=0;dim--)
    d[dim] = a[dim]*b[dim];
  return d;
}

float* vscale(int dim,float a, float* b, float*d){
   for(dim--;dim >=0;dim--)
     d[dim] = a*b[dim];
  return d;
}

float  vdot(int dim,float* a, float* b){
  float sum = 0;
  for(dim--;dim >=0;dim--)
    sum += a[dim]*b[dim];
  return sum;
}

float vangle(int dim,float* a, float* b){
  return acos(vdot(dim,a,b));
}

float* vcross3d(float* a, float* b, float* d){
  d[0] = a[1]*b[2]-a[2]*b[1];
  d[1] = a[2]*b[0]-a[0]*b[2];
  d[2] = a[0]*b[1]-a[1]*b[0];
  return d;
}

int vtoleq(int dim, float* a, float* b){
  for(dim--; dim >=0; dim--)
    if(!toleq(a[dim],b[dim]))
      return 0;
  return 1;
}

float* vnormalize(int dim,float* a, float* d){
  float length = sqrt(vdot(dim,a,a));
  for(dim--; dim >= 0; dim--)
    d[dim] = a[dim]/length;
  return d;
}
