#include"SimpleObject.h"

SimpleObject::SimpleObject():WorldObject(){
}

SimpleObject::SimpleObject(char* filename):WorldObject(filename){
}

void SimpleObject::update(float){
}


//this object never moves so it never impacts anything
float SimpleObject::intersect(float f,
			      WorldObject* wop, 
			      IntersectionInfo* info){ return f; }
void SimpleObject::impactAction(WorldObject* wop,IntersectionInfo* info){}
void SimpleObject::impactReaction(WorldObject* wop,IntersectionInfo* info){}
