#include "Vision.h"

Vision::Vision() {
}

Vision::Vision(int wi, int he, int de, int r, int g, int b) {
  initialize(wi, he, de, r, g, b);
}

Vision::Vision(int wi, int he, int de) {
  initialize(wi, he, de, 0, 1, 2);
}

Vision::~Vision() {
  delete [] image;
}

void Vision::initialize(int wi, int he, int de, int r, int g, int b) {
  width = wi;
  height = he;
  depth = de;
  int rgb_order[3] = {r, g, b};
  for (int d = 0; d < depth; d++)
    // set offsets for RGB
    rgb[d] = rgb_order[d];
  image = new unsigned char [width * height * depth];
  memset(image, 0, width * height * depth);
}

PyObject *Vision::set(int w, int h, int d, int val) {
  if (w < 0 || w >= width ||
      h < 0 || h >= height ||
      d < 0 || d >= depth ||
      val < 0 || val >= 256) {
    PyErr_SetString(PyExc_ValueError, "width, height, depth or value out-of-bounds in set");
    return NULL;
  } else {
    image[(h * width + w) * depth + rgb[d]] = val;
  }
  return Py_BuildValue("i", val);
}

PyObject *Vision::getMMap() {
  PyObject *buffer;
  buffer = PyBuffer_FromMemory(image, 
			       width * height * depth * sizeof(unsigned char));
  return Py_BuildValue("O", buffer);
}


PyObject *Vision::get(int w, int h) {
  if (w < 0 || w >= width ||
      h < 0 || h >= height) {
    PyErr_SetString(PyExc_ValueError, "width or height out-of-bounds in get");
    return NULL;
  }
  if (depth == 3) {
    return Py_BuildValue("iii", 
			 image[(h * width + w) * depth + rgb[0]],
			 image[(h * width + w) * depth + rgb[1]],
			 image[(h * width + w) * depth + rgb[2]] );
  } else if (depth == 1) {
    return Py_BuildValue("i", image[(h * width + w) * depth + 0]);
  } else {
    PyErr_SetString(PyExc_ValueError, "Invalid depth in get");
    return NULL;
  }
}

void Vision::superColor(float w1, float w2, float w3, int outChannel) {
  float weight[3] = {w1, w2, w3};
  for (int w=0; w<width; w++) {
    for (int h=0; h<height; h++) {
      int brightness = 0;
      for (int d = 0; d < depth; d++) {
	// compute brightness as sum of values * weight
	brightness += (int) (image[(h * width + w) * depth + rgb[d]] * weight[rgb[d]]);
	// blacken pixel:
	image[(h * width + w) * depth + rgb[d]] = 0;
      }
      if (brightness > 0)
	// reset outChannel pixel to brightness level:
	image[(h * width + w) * depth + rgb[outChannel] ] = brightness; 
    }
  }
}  

void Vision::filterByColor(int r, int g, int b, int tolerance, 
			   int outChannel) {
  filterByColor( r - tolerance, g - tolerance, b - tolerance,
		 r + tolerance, g + tolerance, b + tolerance,
		 outChannel );
}


void Vision::filterByColor(int lr, int lg, int lb,
			   int hr, int hg, int hb,
			   int outChannel ) {
  int matches;
  for(int h=0;h<height;h++) {
    for(int w=0;w<width;w++) {
      matches = 0;
      if (( image[(h * width + w) * depth + rgb[RED]] >= lr && 
	    image[(h * width + w) * depth + rgb[RED]] <= hr) &&
	  ( image[(h * width + w) * depth + rgb[GREEN]] >= lg && 
	    image[(h * width + w) * depth + rgb[GREEN]] <= hg) &&
	  ( image[(h * width + w) * depth + rgb[BLUE]] >=  lb && 
	    image[(h * width + w) * depth + rgb[BLUE]] <= hb) ) {
	matches = 1;
	/* maybe add a normalizer here so the outputs are 
	   between 100-255ish for more varied usage? */
	for (int d = 0; d < depth; d++) {
	  image[(h * width + w) * depth + rgb[d] ] = 0;
	}
	if (matches)
	  image[(h * width + w) * depth + rgb[outChannel] ] = 255;
      }
    }
  }
}

int Vision::saveImage(char *filename) {
} 

int Vision::getWidth() { return width; }
int Vision::getHeight() { return height; }
int Vision::getDepth() { return depth; }
