#ifndef __VOPS_H
#define __VOPS_H
#ifdef __cplusplus
extern "C" {
#endif

  extern float E0[];
  extern float E1[];
  extern float E2[];
  extern float E3[];
  extern float E4[];
  

  float* vcpy(int dim,float* a, float* d);
  float* vadd(int dim,float* a, float* b, float* d);
  float* vsub(int dim,float* a, float* b, float* d);
  float* vmul(int dim,float* a, float* b, float* d);
  float* vscale(int dim,float a, float* b, float* d);
  float  vdot(int dim,float* a, float* b);
  float  vangle(int dim,float* a, float* b);
  int    vtoleq(int dim, float* a, float* b);
  float* vnormalize(int dim,float* a, float* d);

  
  float* vcross3d(float* a, float* b, float* d);

#define vcpy3d(a,d)   vcpy(3,a,d)
#define vadd3d(a,b,d)   vadd(3,a,b,d)
#define vsub3d(a,b,d)   vsub(3,a,b,d)
#define vmul3d(a,b,d)   vmul(3,a,b,d)
#define vscale3d(a,b,d) vscale(3,a,b,d)
#define vdot3d(a,b)     vdot(3,a,b)
#define vangle3d(a,b)   vangle(3,a,b)





#ifdef __cplusplus
}
#endif

#endif
