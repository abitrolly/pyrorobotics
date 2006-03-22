#include "Stereo.h"

#include <math.h>

Stereo::Stereo(void *left, void *right) {
  // other image:
  Device *leftdevice = (Device *)left;
  Device *rightdevice = (Device *)right;
  leftimage = leftdevice->getImage();
  leftwidth = leftdevice->getWidth();
  leftheight = leftdevice->getHeight();
  leftdepth = leftdevice->getDepth();
  rightimage = rightdevice->getImage();
  rightwidth = rightdevice->getWidth();
  rightheight = rightdevice->getHeight();
  rightdepth = rightdevice->getDepth();
  // this image:
  width = leftwidth;
  height = leftheight;
  depth = leftdepth;
  initialize(width, height, depth, 0, 1, 2);
  updateMMap();
}

PyObject *Stereo::updateMMap() {
  for (int w = 0; w < width; w++) {
    for (int h = 0; h < height; h++) {
      int totalDiff = 0;
      for (int d = 0; d < depth; d++) {
	totalDiff += abs(leftimage[(h * width + w) * depth + d] - rightimage[(h * width + w) * depth + d]);
      }
      for (int d = 0; d < depth; d++) {
	image[(h * width + w) * depth + d] = (unsigned char) fmin(fmax(totalDiff/3, 0), 255);
      }
    }
  } 
  return PyInt_FromLong(0);
}

