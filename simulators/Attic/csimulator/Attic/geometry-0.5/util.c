#include<stdarg.h>
#include<stdio.h>

void swap(int count, float* a, float*b){
  float tmp;
  for(count--; count >= 0; count--){
    tmp = a[count];
    a[count] = b[count];
    b[count] = tmp;
  }
}


int iprint_spaces = 2;
int iprint_level = 0;
void iprintln(char* fmt,...){
  int i,j;
  va_list args;

  va_start(args,fmt);
  
  for(i=0;i<iprint_level; i++)
    for(j=0; j<iprint_spaces; j++)
      printf(" ");

  vprintf(fmt,args);
  printf("\n");

  va_end(args);
}

void iprint(char* fmt,...){
  int i,j;
  va_list args;

  va_start(args,fmt);

  for(i=0;i<iprint_level; i++)
    for(j=0; j<iprint_spaces; j++)
      printf("  ");

  vprintf(fmt,args);

  va_end(args);
}

void iup(){
  iprint_level++;
  if(iprint_level > 5) iprint_level = 5;
}

void idn(){
  iprint_level--;
  if(iprint_level < 0) iprint_level = 0;
}
