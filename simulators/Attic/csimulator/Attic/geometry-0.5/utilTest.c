#include"geometry.h"

void utilTest(){
  float v2d_0[2] = {1,2};
  float v2d_1[2] = {3,4};
  int failure = 0;

  iprintln("Util");
  iup();
    
  iprintln("swap()");
  
  swap(2,v2d_0,v2d_1);
  
  failure |= (v2d_0[0] != 3);
  failure |= (v2d_0[1] != 4);
  failure |= (v2d_1[0] != 1);
  failure |= (v2d_1[1] != 2);
  
  if(failure)
    iprintln("-> swap() failed!");
  
  idn();
}
