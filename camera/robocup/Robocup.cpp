#include "Robocup.h"

Robocup::Robocup(int w, int h, int d) {
  initialize(w, h, 3, 0, 1, 2);
  clear();
}

void Robocup::drawRect(long int left, long int right, 
		    long int top, long int bottom, 
		    long int r, long int g, long int b) {
  for(int w=left; w<=right; w++) {
    for(int h=top; h<=bottom; h++ ) {
      image[(h * width + w) * depth + rgb[0]] = r;
      image[(h * width + w) * depth + rgb[1]] = g;
      image[(h * width + w) * depth + rgb[2]] = b;
    }
  }
}

void Robocup::clear() {
  for(int w=0; w<width; w++) {
    for(int h=0; h<height; h++ ) {
      image[(h * width + w) * depth + rgb[0]] = 0;
      image[(h * width + w) * depth + rgb[1]] = 153;
      image[(h * width + w) * depth + rgb[2]] = 0;
    }
  }
}

PyObject *Robocup::updateMMap(PyObject *robocupData) {
  int r, g, b;
  int x, y;
  char name[25];
  PyObject *points, *lines;
  clear();
  // Takes a dict and a list
  // [{'right': [(4, 12), (31, 12), (15, 12), (20, 12)], 
  //   'center': [(17, 28)], 
  //   'Bottom': [(33, 13), (33, 16), (33, 19)], 
  //   '1pleft': [], 'Left': [], 'Top': [(2, 13), (2, 16)], 'left': []},
  //  [['b', 7.4000000000000004, -44.0, 0, 0]]
  // ]
  if (!PyArg_ParseTuple(robocupData, "OO", &points, &lines)) {
    PyErr_SetString(PyExc_TypeError, "Invalid args to updateMMap((DICT,LIST))");
    return NULL;
  }
  // draw lines
  // draw objects
  for (int objCnt = 0; objCnt < PyList_Size(lines); objCnt++) {
    PyObject *obj = PyList_GetItem(lines, objCnt);
    if (!PyArg_ParseTuple(obj, "sii", name, &x, &y)) {
      PyErr_SetString(PyExc_TypeError, "Invalid list item to updateMMap((DICT,LIST)) where LIST is ((name, x, y)...)");
      return NULL;
    }
    drawRect(x - 1, x + 1, y - 1, y + 1, 128, 128, 128);
  }
  return PyInt_FromLong(0L);
}
