#ifndef __CVXHULL2D_H__
#define __CVXHULL2D_H__

#ifdef __cplusplus
extern "C" {
#endif 


  enum {
	CVXHULL_GIFTWRAP,
	CVXHULL_QUICKHULL,
	CVXHULL_GRAHAMS
	};

  int cvxhull2D(int nPts,float* pts);


#ifndef SWIG
  void cvxhullSetFunc2D(int (*ch)(int nPts, float* pts));
#endif

  void cvxhullSetAlgo2D(int algo);

  int giftWrap2D(int nPts,float* pts);
  int quickHull2D(int nPts,float* pts);
  int grahams(int nPts,float* pts);

#ifdef __cplusplus
}
#endif

#endif
