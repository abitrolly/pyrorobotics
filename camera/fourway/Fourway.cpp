#include "Fourway.h"

Fourway::Fourway(void *odev, 
		 int quad) {
  // other image:
  Device *device = (Device *)odev;
  otherimage = device->getImage();
  otherwidth = device->getWidth();
  otherheight = device->getHeight();
  otherdepth = device->getDepth();
  // this image:
  width = otherwidth/2;
  height = otherheight/2;
  depth = otherdepth;
  quadNumber = quad;
  initialize(width, height, depth, 0, 1, 2);
  updateMMap();
}

PyObject *Fourway::updateMMap() {
  int offset = 0;
  if (quadNumber == 0)
    offset = 0;
  else if (quadNumber == 1)
    offset = width * depth;
  else if (quadNumber == 2)
    offset = height * width * depth * 2;
  else if (quadNumber == 3)
    offset = (height * width * depth * 2) + (width * depth);
  // Copy the image quad to our space:
  for (int h = 0; h < height; h++) {
    for (int w = 0; w < width; w++) {
     for (int d = 0; d < depth; d++) {
       image[(h * width + w) * depth + d] = 
	 otherimage[offset + (h * otherwidth + w) * otherdepth + d];
     }
    }
  } 
  return PyInt_FromLong(0);
}

