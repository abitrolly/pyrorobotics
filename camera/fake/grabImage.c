/* Loads image data from files; stores in map, shared memory space */

#include <Python.h>
#include "../vision/vision.h"

void *map;

static PyObject *grab_image(PyObject *self, PyObject *args){
  char *filename;
  int limit, width, height, num, maxval, color, depth;
  PyObject *buffer, *tuple;
  FILE* theFile;
  
  if(!PyArg_ParseTuple(args, "s", &filename)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to fake_grab_image");
    return NULL;
  }

  theFile = fopen(filename, "r");
  if (!theFile){
    PyErr_SetString(PyExc_IOError, "fake_grab_iamge: Error loading file");
    return NULL;
  }

  fscanf(theFile, "P%d\n%d %d\n%d\n", &num, &width, &height, &maxval);
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
    PyErr_SetString(PyExc_TypeError, "fake_grab_image: Invalid PPM, must be 3 bytes per pixel");
    fclose(theFile);
    return NULL;
  }

  if (color){
    map = malloc(width*height*3);
    fread(map, 1, width*height*3, theFile);
    buffer = PyBuffer_FromMemory(map, width*height*3);
    depth = 3;
  } else{
    map = malloc(width*height);
    fread(map, 1, width*height, theFile);
    buffer = PyBuffer_FromMemory(map, width*height);
    depth = 1;
  }

  tuple = Py_BuildValue("iiiO", width, height, depth, buffer);

  return tuple;
}

static PyObject *refresh_image(PyObject *self, PyObject *args){
  char *filename;
  int width, height, num;
  FILE *theFile;

  if (!PyArg_ParseTuple(args, "s", &filename)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to fake_load_image");
    return NULL;
  }

  theFile = fopen(filename, "r");
  if (!theFile){
    PyErr_SetString(PyExc_IOError, "fake_grab_iamge: Error loading file");
    return NULL;
  }

  fscanf(theFile, "P%d\n%d %d\n%*d\n", &num, &width, &height);
  if (num == 5)
    fread(map, 1, width*height, theFile);
  else
    fread(map, 1, width*height*3, theFile);

  fclose(theFile);

  return PyInt_FromLong(0L);
}

static PyObject *free_image(PyObject *self, PyObject *args){
  free(map);
  return PyInt_FromLong(0L);
}

#include "../vision/vision.c"


static PyMethodDef grabImageMethods[] = {
  {"grab_image", grab_image, METH_VARARGS, "Load up the fake camera"},
  {"refresh_image", refresh_image, METH_VARARGS, "Load another image into the fake camera"},
  {"free_image", free_image, METH_VARARGS, "Free the fake camera"},

#include "../vision/visionMethods.h"

  {NULL, NULL, 0, NULL}
};

void initgrabImage(void){
  (void) Py_InitModule("grabImage", grabImageMethods);
}

