#ifndef __TRIANGLE_H
#define __TRIANGLE_H

#ifdef __cplusplus
extern "C"{
#endif

typedef struct triangleArray{
  int nColor;
  float* color; //4d vectors in a row

  int nVertex;
  float* vertex; //3d vectors in a row

  int nNormal;
  float* normal;

  int nTexCoord;
  float* texCoord;


  int nTriangles;
  int*   tColor;
  int*   tVertex;
  int*   tNormal;
  int*   tTexCoord;
}triangleArray;

#ifdef __cplusplus
}
#endif
#endif
