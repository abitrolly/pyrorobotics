#ifndef __BASICPHYSICSOBJECT_H
#define __BASICPHYSICSOBJECT_H

#ifdef __cplusplus


#include"WorldObject.h"

class BasicPhysicsObject : public WorldObject{
  float location[3];
  float velocity[3];
 public:
  BasicPhysicsObject(char* woFile);
  virtual void update(float dt);
  virtual float intersect(float dt, WorldObject* wop,IntersectionInfo*);
  virtual void impactAction(WorldObject* wop,IntersectionInfo*);
  virtual void impactReaction(WorldObject* wop,IntersectionInfo*);
};

#endif

#endif
 
