#include<malloc.h>
#include<math.h>
#include<assert.h>
#include<stdio.h>

#include"World.h"

World::World(){objects = NULL; infos = NULL; }

void World::addObject(WorldObject* wop){
  nObjects++;
  objects = (WorldObject**) realloc(objects,nObjects*sizeof(WorldObject*));
  objects[nObjects-1] = wop;
  infos = (IntersectionInfo*) realloc(infos,sizeof(IntersectionInfo)*sumOfn_euler(nObjects-1)); 
}

void World::render(unsigned int mode){
    for(int i=0; i<nObjects; i++)
      objects[i]->render(mode);
}

void World::update(float dt){

  float it = 0,mit = HUGE_VAL;

  while(dt > 0){
    //find the minimum time until intersection
    for(int i=0; i<nObjects; i++)
      for(int j=i+1; j<nObjects; j++){
	fprintf(stderr,"max: %d val: %d obj: %p\n",
		sumOfn_euler(nObjects-1),
		sumOfn_euler(i)+(j-i-1),
		objects[j]
		);        
	it = objects[i]->intersect(dt,
				   objects[j],
				   &infos[sumOfn_euler(i)+(j-i-1)]);
	printf("yo 1\n");
	if(it != dt)
	  if(it < mit)
	    mit = it;
      }

    //update time until first intersection
    for(int i=0; i<nObjects; i++)
      objects[i]->update(mit);
    dt -= mit;

    //for each colliding objects do compute collision
    for(int i=0; i<nObjects; i++)
      for(int j=i+1; j<nObjects; j++){
	IntersectionInfo* info = &infos[sumOfn_euler(i)+(j-i-1)];
	if(objects[i]->intersect(dt,
				 objects[j],
				 info) == 0){
	  objects[i]->impactAction(objects[j],info);
	  objects[j]->impactReaction(objects[i],info);
	}
      }
  }

}
