
#ifndef __TRIANGLE_H
#define __TRIANGLE_H

#ifdef __cplusplus

struct Triangle{
  float vertex[3][3]; 
  float normal[3][3];
  float tcoord[3][3];
  float color[3][3];

  void load(int fd);
  void save(int fd);
  void render(); //assumes glBegin has been called.
  int intersect(float pta[3], float ptb[3],float* dist);
};

#endif
#endif
