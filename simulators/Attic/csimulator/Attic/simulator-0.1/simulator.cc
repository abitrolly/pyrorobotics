
#include<GL/gl.h>

#include"simulator.h"


void simulator_test(){
  World* world = new World();

  WorldObject* objects[3] = {
    new BasicPhysicsObject("cube.wo"),
    new BasicPhysicsObject("cube.wo"),
    new BasicPhysicsObject("cube.wo")
  };

  objects[0]->scale(.1,.1,.1);

  objects[1]->scale(.2,.2,.2);
  objects[1]->translate(.3,.3,.3);

  for(int i=0; i<3; i++)
    world->addObject(objects[i]);

  while(1){
    world->update(.001);
    world->render(GL_TRIANGLES);
  }
}
