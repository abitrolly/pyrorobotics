#include"geometry.h"

void volumeTest(){
  float tmp;
  float pt0[3] = {0,0,0};
  float pt1[3] = {1,0,0};
  float pt2[3] = {0,1,0};
  float pt3[3] = {0,0,1};

  iprintln("Volume");
  iup();
  iprintln("volumeTetrahedron()");
  iup();
  tmp = volumeTetrahedron(pt1,pt2,pt3,pt0);
  if(!toleq(tmp,1.0/6.0))
    iprintln("-> volume should be %f but is %f. %d",1.0/6.0,tmp);
  
  tmp = volumeTetrahedron(pt0,pt1,pt2,pt3);
  if(!toleq(tmp,-1.0/6.0))
    iprintln("-> volume should be %f but is %f.",-1.0/6.0,tmp);

  idn();
}
