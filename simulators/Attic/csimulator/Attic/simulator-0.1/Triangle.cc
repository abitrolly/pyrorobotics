#include<unistd.h>
#include<assert.h>
#include<errno.h>
#include<GL/gl.h>

#include"Triangle.h"  
#include<geometry/geometry.h>

void Triangle::render(){
  for(int i=0; i<3; i++){
    glColor3fv(color[i]);
    glTexCoord2fv(tcoord[i]);
    glNormal3fv(normal[i]);
    glVertex3fv(vertex[i]);
  }
}

void Triangle::save(int fd){
  int size = sizeof(Triangle);
  int written = ::write(fd,this,size);
  assert_perror(errno);
  assert(written == size);
}

void Triangle::load(int fd){
  int size = sizeof(Triangle);
  int readten = ::read(fd,this,size);
  assert_perror(errno);
  assert(readten = size);
}

int Triangle::intersect(float* pta, float* ptb, float* time){
  return isectSegTri3d(pta,ptb,
		       vertex[0],vertex[1],vertex[2],
		       time,NULL,NULL);
}
