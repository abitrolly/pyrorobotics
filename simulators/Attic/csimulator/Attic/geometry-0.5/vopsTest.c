#include<math.h>
#include"geometry.h"

void vopsTest(){
  float tmp;
float pt0[3] = {0,0,0};
  float pt1[3] = {1,0,0};
  float pt2[3] = {0,1,0};
  float pt3[3] = {0,0,1};
  float pt4[3] = {1,2,3};
  float pt5[3] = {2,3,4};

  iprintln("Vector Operations");

  iup();
  iprintln("vdot()");
  iup();
  tmp = vdot(3,pt4,pt5);
  if(tmp != (1*2)+(2*3)+(3*4))
    iprintln("-> vdot should be %f but was %f.",(1*2)+(2*3)+(3*4),tmp);
  tmp = vdot(3,pt0,pt4);
  if(tmp != 0)
    iprintln("-> vdot should be %f but was %f.",0,tmp);
  tmp = vdot(3,pt1,pt5);
  if(tmp != 2)
    iprintln("-> vdot should be %f but was %f.",2,tmp);
  idn();

  iprintln("vangle()");
  iup();
  if(!toleq(vangle(3,pt1,pt2),M_PI/2))
    iprintln("-> failed");
  idn();

  iprintln("vcross3d()");
  iup();
  vcross3d(pt1,pt2,pt5);
  if(!vtoleq(3,pt3,pt5))
    iprintln("-> failed. should (%f,%f,%f) was (%f,%f,%f)",pt3[0],pt3[1],pt3[2],pt5[0],pt5[1],pt5[2]);
  idn();

  iprintln("normalize()");
  iup();
  if(!toleq(1,vdot(3,vnormalize(3,pt4,pt4),pt4)))
    iprintln("-> failed");
  idn();

  iprintln("sub()");
  iup();
  if(!vtoleq(3,pt0,vsub(3,pt4,pt4,pt4)))
    iprintln("-> failed    ");
  idn();

  idn();
}
