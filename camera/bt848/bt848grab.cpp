#include "BT848.h"

main(int argc, char *argv[]) {
  char filename[255];
  strcpy(filename, argv[1]);
  BT848 *cam = new BT848( "/dev/bt848fg0", ICOLS, IROWS );
  cam->Update();
  cam->Update();
  cam->Update();
  cam->saveFile(filename);
}
