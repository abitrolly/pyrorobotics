#include<stdio.h>
#include<assert.h>
#include<stdlib.h>
#include"mops.h"
#include"compare.h"

float* melem(int W,int H,int w,int h,float* m){
  return m+H*w+h;
}

float* mcpy(int w, int h, float* a, float* d){
  int i;
  for(i=0; i<w*h; i++)
    d[i] = a[i];

  return d;
}

float* mzero(int w, int h, float* m){
  int i;
  for(i=0; i<w*h; i++)
    m[i] = 0;
  return m;
}

float* mone(int w, int h, float* m){
  int W = w;
  int H = h;

  assert(W==H);

  mzero(W,H,m);

  for(w--; w>=0; w--)
    *melem(W,H,w,w,m)=1;

  return m;
}

float*   mrand(int w, int h, float min, float max, float* m){
  int W = w;
  int H = h;

  assert(max>min);

  for(w--; w>=0; w--){

    for(h=H-1; h>=0; h--){
      *melem(W,H,w,h,m)=((float)rand() / (float) RAND_MAX);
      *melem(W,H,w,h,m)*= max-min;
      *melem(W,H,w,h,m)+= min;
    }
  }
  return m;
}

float* madd(int w, int h, float* a, float* b, float* d){
  int i; 
  for(i=0; i<w*h; i++)
    d[i] = a[i]+b[i];
  return d;
}

float* msub(int w, int h, float* a, float* b, float* d){
  int i; 
  for(i=0; i<w*h; i++)
    d[i] = a[i]-b[i];
  return d;
}

float* mmul(int wa, int ha, int wb, int hb, float* a, float* b, float* d){
  int c,r,e;
  assert(wa == hb);

  mzero(wb,ha,d);

  for(c=0; c<wb; c++) // each column of b
    for(r=0; r<ha; r++)// each row of a
      for(e=0; e<wa; e++) // each element 
	d[c*wb+r] += a[e*ha+r]*b[c*hb+e];

  return d;
}

float* minv(int w, int h, float* a, float* t,float* d){
  //make temp matrix
  float scale;
  int i,j,diag;

  //initialize, dont break a
  mcpy(w,h,a,t );
  mone(w,h,d);


  for(diag=0; diag<h; diag++){ //for each element in the diagonal

    scale = t[diag*h+diag];     //make diagnal element 1
    assert(scale != 0); 
    for(j=0; j<h; j++){    
      t[j*h+diag]   /= scale;
      d[j*h+diag]   /= scale;
    }

    for(i=0; i<h; i++){
      if(i==diag) continue;

      scale = t[diag*h+i];

      for(j=0; j<w; j++){
	t[j*h+i] -= scale*t[j*h+diag];
	d[j*h+i] -= scale*d[j*h+diag];
      }
    }
  }

  return d;
}

/*
float* mmulv(int w, int h,float* m, float* v,float* d){
  assert(0);
  return d;
}
*/

float* vmulm(int w, int h,float*  v,float* m,float* d){
  assert(0);
  return d;
}

int mequ(int w, int h, float* a, float* b){
  int i;
  for(i=0; i<w*h; i++)
    if(!toleq(a[i],b[i]))
      return 0;
  return 1;
}

float* mscale(int w, int h, float s, float* m){
  int i;
  for(i=0; i<w*h; i++)
    m[i] *= s;
  return m;
}



void mshow(int w, int h,float* a,char* prefix){
  int i,j;

  for(j=0; j<h; j++){
    printf("%s|",prefix);
    for(i=0; i<w; i++){
      printf("%3.4f",*melem(w,h,i,j,a));
      if((i+1) != w)
	printf(" ");
    }
      printf("|\n");
  }
}
