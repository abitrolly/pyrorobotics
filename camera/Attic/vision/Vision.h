#ifndef __VISION_H__ 
#define __VISION_H__ 

#include <Python.h>

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


#define SWAP(a,b) { int itemp=(a);(a)=(b);(b)=itemp;}
#define MAXBLOBS 2000

class Vision {
  static const int RED = 0;
  static const int GREEN = 1;
  static const int BLUE = 2;
  
public:
  Vision();
  Vision(int w, int h, int d, int r, int g, int b);
  Vision(int w, int h, int d);
  ~Vision();
  void initialize(int wi, int he, int de, int r, int g, int b);
  void superColor(float w1, float w2, float w3,
		  int outChannel);
  void filterByColor(int lr, int lg, int lb,
		     int hr, int hg, int hb,
		     int outChannel);
  void filterByColor(int r, int g, int b, int tolerance, 
		     int outChannel);
  PyObject *get(int w, int h);
  PyObject *set(int w, int h, int d, int val);
  void drawRect(int x1, int y1, int x2, int y2, 
		int fill, int channel);
  void meanBlur(int kernel);

  int getWidth();
  int getHeight();
  int getDepth();
  PyObject *saveImage(char *filename);
  PyObject *getMMap();

  unsigned char *image;


  PyObject *Vision::colorHistogram();
  PyObject *Vision::trainColor();
  void gaussianBlur();
  void grayScale(int value);
  PyObject *sobel(int val);
  void medianBlur(int kernel);
  void clear(int channel, int value);

  Blob *initBlob(Blob *b);
  Blob *initBlob( Blob *b, int y, int x );
  Blob *addPixel( Blob *b, int y,int x );
  void joinBlob( Blob *self, Blob *other );
  void deleteBlob( Blob *b );
  int getBlobWidth( Blob *b );
  int getBlobHeight( Blob *b );
  int getBlobArea( Blob *b );
  void sortBlobs(int sortMethod, Blob bloblist[], int indexes[], int size);
  PyObject *blobify(int inChannel, int low, int high, 
			    int sortmethod, 
			    int size, int drawBox);
  PyObject *applyFilters(PyObject *filterList);
  PyObject *addFilter(PyObject *newFilter);
  PyObject *applyFilterList();
  PyObject *setFilterList(PyObject *filterList);
  PyObject *filterList;

 protected:
  int width;
  int height;
  int depth;
  int rgb[3];
};

#endif
