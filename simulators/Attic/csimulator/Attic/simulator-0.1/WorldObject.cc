

#include"WorldObject.h"

#include<errno.h>
#include<fcntl.h>
#include<sys/types.h>
#include<assert.h>
#include<unistd.h>
#include<stdio.h>

#include<GL/gl.h>



WorldObject::WorldObject()
  : HLXform(),
    TriangleList(){
  
}

WorldObject::WorldObject(char* file){
  int fd = open(file,O_RDONLY);
  assert_perror(errno);
  load(fd);
  close(fd);
}

void WorldObject::render(GLenum mode){
  glPushMatrix();
  HLXform::rmulGL();
  TriangleList::render(mode);
  glPopMatrix();
}

int WorldObject::intersect(float* from, float* to,
			   IntersectionInfo* info){


  float realFrom[3];
  float realTo[3];
  
  HLXform::lave(from,realFrom);
  HLXform::lave(to,realTo);


  return TriangleList::intersect(realFrom,realTo,
				 &info->tlIsect,&info->tIsect,
				 &info->distance);
}


void WorldObject::save(int fd){
  HLXform::save(fd);
  TriangleList::save(fd);
}

void WorldObject::load(int fd){
  HLXform::load(fd);
  TriangleList::load(fd);
}
