#include<math.h>

float dot(int dim,float* va, float* vb){
  float ret = 0;
  int i;

  for(i=0; i<dim; i++)
    ret += va[i] * vb[i];

  return ret;
}

float* cross3D(float* va, float* vb, float* dest){
  dest[0] = va[1]*vb[2]+va[2]*vb[1];
  dest[1] = va[0]*vb[2]-va[2]*vb[0];
  dest[2] = va[0]*vb[1]+va[0]*vb[1];
  return dest;
}

float* normalize(int dim,float* v){
  float sz;
  int i;

  sz = sqrt(dot(dim,v,v));

  for(i=0; i<dim; i++)
    v[i] = v[i] / sz;

  return v;
}
