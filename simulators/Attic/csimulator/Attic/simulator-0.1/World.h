#ifndef __WORLD_H
#define __WORLD_H

#include"WorldObject.h"

#ifdef __cplusplus

class World{
 protected:
  int nObjects;
  WorldObject** objects;
  IntersectionInfo* infos;
 public:
  World();
  void addObject(WorldObject*);
  virtual void render(unsigned int mode);
  virtual void update(float dt);
};

#endif
#endif
