#include "V4L.h"

V4L::V4L(char *device_name, int wi, int he, int de, int ch) {

  device = device_name;
  width = wi;
  height = he;
  depth = de;
  channel = ch;
  int color = 0;
  if (depth == 1)
    color = 0;
  else if (depth == 3) 
    color = 1;
  v4ldev = Cgrab_image(device, width, height, depth, channel);

  if (v4ldev == NULL){
    PyErr_SetString(PyExc_IOError, "Error in C function call");
  }
  image = (unsigned char *) v4ldev->data;
}

void V4L::updateMMap() {

  if(Crefresh_image(v4ldev, width, height)){
    PyErr_SetString(PyExc_IOError, "Error in C function call");
  }

}
