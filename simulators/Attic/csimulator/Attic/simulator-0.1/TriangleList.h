#ifndef __TRIANGLEMODEL_H
#define __TRIANGLEMODEL_H

#include"Triangle.h"

#ifdef __cplusplus

class TriangleList {
protected:
  int nTriangles;
  Triangle*  triangles;
  int texture;
public:
  TriangleList();
  void addTriangle(Triangle*);
  void load(int fd);
  void save(int fd);
  virtual void render(unsigned int mode);
  virtual int intersect(float* from, float* to,
			TriangleList** tlIsect,
                        Triangle** tIsect,
                        float* distance);
};


#endif
#endif
