#include<stdlib.h>
#include<fcntl.h>
#include<unistd.h>
#include<sys/types.h>
#include<errno.h>
#include<assert.h>
#include<stdio.h>
#include"simulator.h"


void makeCube(){
  Triangle* triangles = new Triangle[12];
  
  float cube[4][3] = {
    {-1,-1,-1},
    { 1, 1,-1},
    { 1,-1, 1},
    {-1, 1, 1}
  };

  for(int i=0; i<4; i++)
    for(int t=0; t<3; t++)
      for(int v=0; v<3; v++)
        for(int d=0; d<3; d++){
          triangles[i*3+t].vertex[v][d] =
            ( ((v==0) || ((v+d+t)%3))
              ? 1 : -1 ) * cube[i][d];
          triangles[i*3+t].normal[v][d] = ((d+t)%3)
            ? 0 : cube[i][d-3];
	}
  
  WorldObject* model = new SimpleObject();

  for(int i=0; i<12; i++)
    model->addTriangle(triangles+i);

  int fd = open("cube.wo",O_WRONLY|O_CREAT,0644);
  assert_perror(errno);

  model->save(fd);
  
  close(fd);

  delete model;
  delete[] triangles;
}



int main(int,char**){
  makeCube();
  return 0;
}
