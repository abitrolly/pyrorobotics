#ifndef __UTIL_H__
#define __UTIL_H__

#ifdef __cplusplus
extern "C" {
#endif

  void swap(int count,float* a, float* b);

#ifndef SWIG
  void iprintln(char* fmt,...);
  void iprint(char* fmt,...);
  void iup();
  void idn();
#endif

#ifdef __cplusplus
}
#endif 

#endif

