#ifndef __WORLDOBJECT_H
#define __WORLDOBJECT_H

#include<geometry/geometry.h>
#include"TriangleList.h"
#include"IntersectionInfo.h"

#ifdef __cplusplus

class WorldObject : public HLXform, public TriangleList{
 public:
  WorldObject();
  WorldObject(char* file);
  virtual void render(unsigned int mode);
  virtual void update(float dt)=0;
  virtual int  intersect(float* from, float* to,
			 IntersectionInfo* info);

  //handles intersection between this (the moving object) and wop (the stationary object). The child implementation should deal with the object's motion, eg: turning dt into a line segment and then intersecting that with the passed wop using intersect(float*,float*,info).
  virtual float intersect(float dt, WorldObject* wop,IntersectionInfo*)=0;

  //called when this hits wop

  virtual void impactAction(WorldObject* wop,IntersectionInfo*)=0;
  //called when wop hits this
  virtual void impactReaction(WorldObject* wop,IntersectionInfo*)=0;

  void load(int fd);
  void save(int fd);
};


#endif
#endif
