#include"geometry.h"

void mopsTest(){

  float a[16];
  float b[16];
  float c[16];
  float d[16];
  int i,j;

  iprintln("Matrix");
  iup();
  
  mone4x4(a); mone4x4(b); 

  iprintln("mshow() (melem())");
  mshow4x4(a,"\t");

  iprintln("mequ()");
  if(!mequ4x4(a,b))
    iprintln("-> failed  ");

  iprintln("mmul()");
  mmul4x4(a,b,d);
  if(!mequ4x4(a,d))
    iprintln("->failed  ");

  for(i=0; i<4; i++) //something not identity times identity
    for(j=0; j<4; j++)
      *melem4x4(i,j,a) = 1;
  mmul4x4(a,b,d);
  if(!mequ4x4(a,d))
    iprintln("->failed ");

  iprintln("mscale() and madd()");
  mone4x4(a);
  madd4x4(a,b,d);
  mscale4x4(2,a);
  if(!mequ4x4(a,d))
    iprintln("->failed  ");

  iprintln("minv()");

  *melem4x4(0,0,a) = 1;  
  *melem4x4(0,1,a) = 3;
  *melem4x4(0,2,a) = 0;
  *melem4x4(0,3,a) = 0;
  *melem4x4(1,0,a) = 2;
  *melem4x4(1,1,a) = 1;
  *melem4x4(1,2,a) = 0;
  *melem4x4(1,3,a) = 0;
  *melem4x4(2,0,a) = 0;
  *melem4x4(2,1,a) = 0;
  *melem4x4(2,2,a) = 1;
  *melem4x4(2,3,a) = 0;
  *melem4x4(3,0,a) = 0;
  *melem4x4(3,1,a) = 0;
  *melem4x4(3,2,a) = 0;
  *melem4x4(3,3,a) = 1;
  mrand4x4(-1,1,a);

  minv4x4(a,b,d);
  mmul4x4(a,d,b);
  mone4x4(c);

  if(!mequ4x4(b,c)){
    iprintln("->failed  ");
    iprintln("A");
    mshow4x4(a,"\t");
    iprintln("A^-1");
    mshow4x4(d,"\t");
    iprintln("A*A^-1");
    mshow4x4(b,"\t");
    iprintln("1");
    mshow4x4(c,"\t");
  }

  idn();
}
