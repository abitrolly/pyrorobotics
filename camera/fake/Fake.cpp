#include "Fake.h"

Fake::Fake(char filename[]) {
  int limit, w, h, num, maxval, color, d;
  PyObject *buffer, *tuple;
  FILE* theFile;
  theFile = fopen(filename, "r");
  if (!theFile){
    PyErr_SetString(PyExc_IOError, "Fake: Error loading file");
  }
  fscanf(theFile, "P%d\n%d %d\n%d\n", &num, &w, &h, &maxval);
  fclose(theFile);
  switch(num){
  case 5:
    color = 0;
    break;
  case 6:
    color = 1;
    break;
  default:
    color = 1;
  }
  if (maxval > 255){
    PyErr_SetString(PyExc_TypeError, "Fake: Invalid PPM, must be 3 bytes per pixel");
  }
  if (color){
    initialize(w, h, 3, 0, 1, 2);
  } else{
    initialize(w, h, 1, 0, 0, 0);
  }
  updateMMap(filename);
}

PyObject *Fake::updateMMap(char filename[]) {
  int w, h, num;
  FILE *theFile;
  theFile = fopen(filename, "r");
  if (!theFile){
    PyErr_SetString(PyExc_IOError, "Fake: Error loading file");
    return NULL;
  }
  fscanf(theFile, "P%d\n%d %d\n%*d\n", &num, &w, &h);
  if (w != width || h != height || 
      (num == 5 && depth != 1) ||
      (num != 5 && depth != 3)){
    PyErr_SetString(PyExc_IOError, "Fake: can't change image type or size");
    fclose(theFile);
    return NULL;
  }
  if (num == 5) {
    fread(image, 1, w * h, theFile);
  } else {
    fread(image, 1, w * h * 3, theFile);
  }
  width = w;
  height = h;
  fclose(theFile);
  return PyInt_FromLong(0L);
}

