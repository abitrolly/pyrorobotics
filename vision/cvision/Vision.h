#ifndef __VISION_H__ 
#define __VISION_H__ 

#include <Python.h>
#include <Device.h>

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
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAXBLOBS 2000

class Vision {
public:
  static const int RED = 0;
  static const int GREEN = 1;
  static const int BLUE = 2;
  static const int ALL = 10;

  static const int WORKSPACE = 50;
  static const int ORIGINAL = 60;
  static const int IMAGE = 70;

  static const int AND = 100;
  static const int OR = 101;
  static const int XOR = 102;
  static const int ACCUM = 103;
  
  Vision();
  Vision(int w, int h, int d, int r, int g, int b);
  Vision(int w, int h, int d);
  ~Vision();
  PyObject *initialize(int wi, int he, int de, int r, int g, int b);
  PyObject *registerCameraDevice(void *args);
  //PyObject *registerCameraDevice(Device device);
  PyObject *superColor(float w1, float w2, float w3,
		  int outChannel);
  PyObject *matchRange(int lr, int lg, int lb,
		       int hr, int hg, int hb,
		       int outChannel);
  PyObject *match(int r, int g, int b, int tolerance,
		  int outChannel);
  PyObject *get(int w, int h);
  PyObject *set(int w, int h, int d, int val);
  PyObject *drawRect(int x1, int y1, int x2, int y2, 
		int fill, int channel);
  PyObject *scale(float r, float g, float b);
  PyObject *meanBlur(int kernel);
  PyObject *gaussianBlur();
  PyObject *medianBlur(int kernel);
  PyObject *threshold(int channel, int value);
  int getMiddleIndex(int median[4][400], int kernel);
  PyObject *inverse(int channel);
  int getWidth();
  int getHeight();
  int getDepth();
  PyObject *saveImage(char *filename);
  PyObject *getMMap();

  PyObject *colorHistogram();
  PyObject *trainColor(int x1, int y1, int x2, int y2, int bins);
  PyObject *grayScale();
  PyObject *sobel(int val);
  PyObject *setPlane(int d, int value);
  PyObject *blobify(int inChannel, int low, int high, 
			    int sortmethod, 
			    int size, int drawBox);
  PyObject *applyFilters(PyObject *filterList);
  PyObject *addFilter(PyObject *newFilter);
  PyObject *applyFilterList();
  PyObject *setFilterList(PyObject *filterList);
  PyObject *getFilterList();
  PyObject *popFilterList();

  int getCopyMode() { return copyMode; }
  void setCopyMode(int value) {copyMode = value;}
  int getMotionDetection() { return motionDetection; }
  void setMotionDetection(int val) { motionDetection = val; }
  PyObject *getRGB();
  PyObject *setRGB(int r, int g, int b); 

  PyObject *setImage(int newImage);
  PyObject *backup();
  PyObject *restore();
  PyObject *motion();

 protected:
  unsigned char *Image; // current image (image, original, workspace)
  unsigned char *image;
  unsigned char *original;
  unsigned char *workspace;
  int copyMode;

  PyObject *filterList;
  int width;
  int height;
  int depth;
  int rgb[3];
  int motionDetection;

  Blob *initBlob(Blob *b);
  Blob *initBlob( Blob *b, int y, int x );
  Blob *addPixel( Blob *b, int y,int x );
  void joinBlob( Blob *self, Blob *other );
  void deleteBlob( Blob *b );
  int getBlobWidth( Blob *b );
  int getBlobHeight( Blob *b );
  int getBlobArea( Blob *b );
  void sortBlobs(int sortMethod, Blob bloblist[], int indexes[], int size);
  PyObject *copy(int);
};

#endif
