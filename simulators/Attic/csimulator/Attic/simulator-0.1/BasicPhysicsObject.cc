
#include "BasicPhysicsObject.h"

#include<assert.h>
#include<stdio.h>

 BasicPhysicsObject::BasicPhysicsObject(char* file)
:WorldObject(file){
  for(int i=0; i<3; i++)
    location[i] = velocity[i] = 0;
}

void BasicPhysicsObject::update(float dt){
  float dpos[3];
  for(int i=0; i<3; i++)
    dpos[i] += dt*velocity[i];

  //update our matrix representation of our position
  translate(dpos[0],dpos[1],dpos[2]);

  //figure out where that puts us
  eval(location,location); 
}

float BasicPhysicsObject::intersect(float dt,WorldObject* wop,IntersectionInfo* info){

  float to[3];

  for(int i=0; i<3; i++)
    to[i] = location[i] + dt*velocity[i];
  
    wop->intersect(location,to,info);



  return info->distance;
}

void BasicPhysicsObject::impactAction(WorldObject* wop,
				      IntersectionInfo* info){
  assert(0);
}

void BasicPhysicsObject::impactReaction(WorldObject* wop,
					IntersectionInfo* info){
  assert(0);
}
