#ifndef __VISION__
#define __VISION__

typedef struct bitmap
{
  int height;
  int width;
  int depth;
  unsigned int data[384][240];
  int *equivList;
}Bitmap;


typedef struct point{
  int x;
  int y;
} Point;


typedef struct blob{

  Point ul;
  Point lr;
  Point cm;

  int mass;
  int next;
}Blob;

#define BLUE     0
#define GREEN    1
#define RED      2
#define MAXBLOBS 2000

#define SWAP(a,b) { int itemp=(a);(a)=(b);(b)=itemp;}

static PyObject *super_red(PyObject *self, PyObject *args);
static PyObject *super_blue(PyObject *self, PyObject *args);
static PyObject *super_green(PyObject *self, PyObject *args);
static PyObject *super_magenta(PyObject *self, PyObject *args);
static PyObject *super_yellow(PyObject *self, PyObject *args);
static PyObject *super_cyan(PyObject *self, PyObject *args);
static PyObject *color_filter(PyObject *self, PyObject *args);
static PyObject *blobify(PyObject *self, PyObject *args);
static PyObject *mean_blur(PyObject *self, PyObject *args);
static PyObject *color_histogram(PyObject *self, PyObject *args);
static PyObject *train_color(PyObject *self, PyObject *args);
static PyObject *gaussian_blur(PyObject *self, PyObject *args);
static PyObject *save_image(PyObject *self, PyObject *args);
static PyObject *grey_scale(PyObject *self, PyObject *args);
static PyObject *sobel(PyObject *self, PyObject *args);
static PyObject *median_blur(PyObject *self, PyObject *args);

#endif
