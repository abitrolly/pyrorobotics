#include<unistd.h>
#include<stdio.h>
#include<malloc.h>
#include<fcntl.h>
#include<assert.h>
#include<errno.h>
#include<values.h>
#include<string.h>
#include<GL/gl.h>

#include"TriangleList.h"

TriangleList::TriangleList(){
  nTriangles = 0;
  triangles = NULL;
  texture = 0;
}

void TriangleList::addTriangle(Triangle* t){
  nTriangles++;
  triangles = (Triangle*) realloc(triangles,nTriangles*sizeof(Triangle));
  memcpy(triangles+nTriangles-1,t,sizeof(Triangle));
}

void TriangleList::load(int fd){
  int size = sizeof(nTriangles);
  int loaded = read(fd,&nTriangles,size);

  assert_perror(errno);
  assert(loaded == size);

  triangles = (Triangle*) realloc(triangles,sizeof(Triangle)*nTriangles);
  for(int i=0; i<nTriangles;i++)
    (triangles+i)->load(fd);
}

void TriangleList::save(int fd){
  int size = sizeof(nTriangles);
  int saved = write(fd,&nTriangles,size);

  assert_perror(errno);
  assert(saved == size);

  for(int i=0; i<nTriangles;i++)
    (triangles+i)->save(fd);
}

void TriangleList::render(unsigned int mode){
  glBindTexture(GL_TEXTURE_2D,texture);
  glBegin(mode);
  for(int i=0; i<nTriangles; i++)
    (triangles+i)->render();
  glEnd();
}

int TriangleList::intersect(float* from, float* to,
			    TriangleList** tlIsect,
			    Triangle** tIsect,
			    float* distance){
  *distance = FLT_MAX;
  float tmpDistance;
  tmpDistance = tmpDistance;
  for(int i=0; i<nTriangles; i++)
    if(triangles[i].intersect(from,to,&tmpDistance))
      if(tmpDistance < *distance){
	*distance = tmpDistance;
	 *tIsect = triangles+i;
	*tlIsect = this;
      }

  if(*distance != FLT_MAX)
    return 1;
  else return 0;
}

