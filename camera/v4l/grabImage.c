#include <Python.h>
#include "v4lcap.h"

static PyObject *grab_image(PyObject *self, PyObject *args){
  char *device;
  int width, height;
  struct image_cap *image;
  PyObject *buffer;

  //Expects grab_image(device_name, width, height)
  if (!PyArg_ParseTuple(args, "sii", &device, &width, &height))
    return NULL;


  
  image = Cgrab_image(device, width, height);
  if (image == NULL){
    return NULL;
  }

  buffer = PyBuffer_FromMemory(image->data, image->size);

  free(image);

  return buffer;
}

//Free the buffer given by grab_image
//Expects free_image(buffer)
static PyObject *free_image(PyObject *self, PyObject *args){
  PyObject *obj, *buffer;
  void *imageptr;
  int size;

  //Get the buffer object from the arguments
  if (!PyArg_ParseTuple(args, "O", &obj)){
    return NULL;
  }

  //Make sure it's a valid buffer object
  if (!PyBuffer_Check(obj))
    return NULL;

  //Convert the object to a buffer object
  buffer = PyBuffer_FromObject(obj, 0, Py_END_OF_BUFFER);

  //This shouldn't be an error if the object passes the previous check
  if (buffer->ob_type->tp_as_buffer->bf_getreadbuffer == NULL)
    return NULL;


  size = (int)(buffer->ob_type->tp_as_buffer->bf_getreadbuffer)(buffer, 0, &imageptr);
  free(imageptr);

  return PyInt_FromLong(0L);
}

static PyMethodDef grabImageMethods[] = {
  {"grab_image", grab_image, METH_VARARGS, "Grab an image from the camera"},
  {"free_image", free_image, METH_VARARGS, "Free memory from a grabbed image"},
  {NULL, NULL, 0, NULL}
};

void initgrabImage(void){
  (void) Py_InitModule("grabImage", grabImageMethods);
}
