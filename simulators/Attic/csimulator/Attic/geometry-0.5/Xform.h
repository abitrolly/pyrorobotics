#ifndef __TRANSFORM_H
#define __TRANSFORM_H

#ifdef __cplusplus

class HLXform{
  float* matrix;
  int inverseIsValid;
  float* inverse;
  float* tmp0,*tmp1;  
 public:
  HLXform();
  void load(int fd);
  void save(int fd);
  void identity();
  void translate(float x,float y, float z);
  void rotate(float theta, float i, float j, float k);
  void scale(float x, float y, float z);
  float* eval(float* v,float* d);
  float* lave(float* v, float* d);
  #ifdef __USE_GL
  void rmulGL(); // right mul gl matrix stack by this xform
  #endif
};

#endif

#endif
