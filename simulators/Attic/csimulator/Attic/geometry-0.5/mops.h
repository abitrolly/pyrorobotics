#ifndef __MOPS_H
#define __MOPS_H


#ifdef __cplusplus
extern "C" {
#endif

  //matrix stored as column vectors. >->-> matrix[w][h]
  float* melem(int W,int H,int w, int h, float* m);

  float* mcpy(int w, int h, float* a, float* d);
  float* mzero(int w,int h, float* m);
  float* mone(int w, int h, float* m);
  float* mrand(int w, int h, float min, float max, float* m);
  float* madd(int w, int h, float* a, float* b, float* d);
  float* msub(int w, int h, float* a, float* b, float* d);
  float* minv(int w, int h, float* a, float* tmp, float* d);
  float* mscale(int w, int h, float s, float* m);
  int    mequ(int w, int h, float* a, float* b);
  void   mshow(int w, int h, float* a,char* prefix);


  //below functions require d != a, d != b
  float* mmul(int w0, int h0, 
	      int w1, int h1,
	      float* a, float* b, 
	      float* d);

  //below functions require d != v
  #define mmulv(w,h,m,v,d) mmul(w,h,1,w,m,v,d)
  //  float* mmulv(int w, int h,float* m, float* v,float* d);
  float* vmulm(int w, int h,float*  v,float* m,float* d);

  //shortcut defines for 4x4 matrices
#define melem4x4(w,h,m) melem(4,4,w,h,m)
#define mzero4x4(m)     mzero(4,4,m)
#define mone4x4(m)      mone(4,4,m)
#define mrand4x4(min,max,m)     mrand(4,4,min,max,m);
#define madd4x4(a,b,d)  madd(4,4,a,b,d)
#define msub4x4(a,b,d)  msub(4,4,a,b,d)
#define mmul4x4(a,b,d)  mmul(4,4,4,4,a,b,d)
#define mmulv4x4(m,v,d) mmulv(4,4,m,v,d)
#define vmulm4x4(v,m,d) vmulm(4,4,v,m,d)
#define mcpy4x4(a,d)    mcpy(4,4,a,d)
#define minv4x4(a,tmp,d)    minv(4,4,a,tmp,d)
#define mequ4x4(a,b)    mequ(4,4,a,b)
#define mshow4x4(a,p)   mshow(4,4,a,p)
#define mscale4x4(s,a)  mscale(4,4,s,a)
#ifdef __cplusplus
}
#endif

#endif
