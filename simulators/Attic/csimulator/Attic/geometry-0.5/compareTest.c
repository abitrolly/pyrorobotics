#include"geometry.h"

void compareTest(){
  iprintln("Compare ");
  iup();
  iprintln("toleq() (macro)");
  if(toleq(1,1+2*TOLERANCE))
    iprintln("-> failed: was equal when should not have been");  
  if(toleq(1,1-2*TOLERANCE))
    iprintln("-> failed: was equal when should not have been");
  if(!toleq(1,1+TOLERANCE/2))
    iprintln("-> failed: was not equal when should have been");
  if(!toleq(1,1-TOLERANCE/2))
    iprintln("-> failed: was not equal when should have been");
  idn();
}
