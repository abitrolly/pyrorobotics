#ifndef __SIMPLEOBJECT_H
#define __SIMPLEOBJECT_H

#ifdef __cplusplus

#include"WorldObject.h"

class SimpleObject : public WorldObject{
 public:
  SimpleObject();
  SimpleObject(char* filename);
  virtual void update(float);
  virtual float intersect(float,WorldObject*,IntersectionInfo*);
  virtual void impactAction(WorldObject* wop,IntersectionInfo*);
  virtual void impactReaction(WorldObject* wop,IntersectionInfo*);
};

#endif

#endif
