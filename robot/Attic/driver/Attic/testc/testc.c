#include<unistd.h>
#include<pthread.h>
#include<stdlib.h>
#include<math.h>
#include"testc.h"



Pi* new_Pi(){
  Pi* pp = (Pi*) malloc(sizeof(Pi));
  pp->value = M_PI;
  return pp;
}

RandomVector* new_RandomVector(){
  RandomVector* rvp = (RandomVector*) malloc(sizeof(RandomVector));

  rvp->x = rvp->y = rvp->z = 0;
  rvp->stop = 0;
  rvp->isStopped = 0;
  pthread_create(&rvp->thread,NULL,randomVectorThread,rvp);

  return rvp;
}

void del_Pi(Pi* pp){
  free(pp);
}

void del_RandomVector(RandomVector* rvp){
  rvp->stop = 1;
  while(!rvp->isStopped)
    sleep(1);
  free(rvp);
}

void* randomVectorThread(void* vrvp){
  float len;
  RandomVector* rvp = (RandomVector*) vrvp;
  while(!rvp->stop){
    rvp->x += ((float)random()/(float)RAND_MAX)/100;
    rvp->y += ((float)random()/(float)RAND_MAX)/100;
    rvp->z += ((float)random()/(float)RAND_MAX)/100;

    len = rvp->x+rvp->y+rvp->z; //normalize by manhattan metric

    if(len < .01) 
      len = .01; // make sure no div by anything close to 0

    rvp->x /= len;
    rvp->y /= len; 
    rvp->z /= len;

    sleep(1);
  }
  rvp->isStopped = 1;
}
