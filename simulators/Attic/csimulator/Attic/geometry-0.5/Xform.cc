#include<assert.h>
#include<malloc.h>
#include<unistd.h>
#include<errno.h>

#include"Xform.h"
#include"mops.h"




HLXform::HLXform(){
  matrix = (float*) malloc(16*sizeof(float));
  inverse = (float*) malloc(16*sizeof(float));
  tmp0 = (float*) malloc(16*sizeof(float));
  tmp1 = (float*) malloc(16*sizeof(float));
  mone4x4(matrix);
  inverseIsValid = 0;
}

void HLXform::load(int fd){
  inverseIsValid = 0;
  int size = sizeof(float)*16;
  int reaten = read(fd,matrix,size);
  assert_perror(errno);
  assert(reaten == size);
}

void HLXform::save(int fd){
  int size = sizeof(float)*16;
  int written = write(fd,matrix,size);
  assert_perror(errno);
  assert(written == size);
}

void HLXform::identity(){
  mone4x4(matrix); 
  mone4x4(inverse);
  inverseIsValid = 1;
}

void HLXform::translate(float x, float y, float z){
  mone4x4(tmp0);
  *melem4x4(0,3,tmp0) = x;
  *melem4x4(1,3,tmp0) = y; 
  *melem4x4(2,3,tmp0) = z;
  mmul4x4(matrix,tmp0,tmp1);
  mcpy4x4(tmp1,matrix);  
  inverseIsValid = 0;
}

void HLXform::rotate(float theta,float i, float j, float k){
  assert(0);
  inverseIsValid = 0;
}

void HLXform::scale(float x, float y, float z){
  mone4x4(tmp0);
  *melem4x4(0,0,tmp0) = x;
  *melem4x4(1,1,tmp0) = y; 
  *melem4x4(2,2,tmp0) = z;
  mmul4x4(matrix,tmp0,tmp1);
  mcpy4x4(tmp1,matrix);
  inverseIsValid = 0;
}

float* HLXform::eval(float* v, float* d){
  int i;
  float tmp[4];
  
  for(i=0; i<3; i++)
    tmp[i] = v[i];
  
  tmp[3] = 1;

  mmulv4x4(matrix,v,tmp);

  for(i=0; i<3; i++)
    d[i] = tmp[i]/tmp[3];

  return d;
}

float* HLXform::lave(float* v, float* d){
  int i;
  float tmp[4];

  for(i=0; i<3; i++)
    tmp[i] = v[i];

  tmp[3] = 1;

  if(!inverseIsValid){
    minv4x4(matrix,tmp0,inverse);
    inverseIsValid = 1;
  }

  mmulv4x4(inverse,tmp,tmp);

  for(i=0; i<3; i++)
    d[i] = tmp[i]/tmp[3];

  return d;
}

#ifdef __USE_GL

void HLXform::rmulGL(){
	assert(0);
}

#endif
