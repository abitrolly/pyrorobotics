#include "BT848.h"

main(int argc, char *argv[]) {
  char number[80];
  strcpy(number, argv[1]);
  BT848 *cam = new BT848( "/dev/bt848fg0", ICOLS, IROWS );
  cam->Update();
  cam->Update();
  cam->Update();
  char buffer[80];
  sprintf(buffer, "som-%s.ppm", number);
  cam->saveFile(buffer);
}
