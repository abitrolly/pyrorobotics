
#ifndef __INTERSECTIONINFO_H

#ifdef __cplusplus

#include"Triangle.h"
#include"TriangleList.h"

struct IntersectionInfo{
  int intersection;
  Triangle* tIsect;
  TriangleList* tlIsect;
  float distance;
};

#endif
#endif
