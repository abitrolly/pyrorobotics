#ifndef __TESTC_H__
#define __TESTC_H__

#include<pthread.h>

typedef
struct {
  float value;
}Pi;

typedef
struct {
  pthread_t thread;
  int stop;
  int isStopped;
  float x,y,z;
}RandomVector;


Pi* new_Pi();
RandomVector* new_RandomVector();

void del_Pi(Pi*);
void del_RandomVector(RandomVector*);

void* randomVectorThread(void*);


#endif __TESTC_H__
