#include "Blob.h"

Blob::Blob(int w, int h, int d) {
  initialize(w, h, 3, 0, 1, 2);
}

PyObject *Blob::updateMMap(PyObject *blobData) {
  return PyInt_FromLong(0L);
}

