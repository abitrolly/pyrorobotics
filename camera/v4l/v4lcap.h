#ifndef __V4LCAP__
#define __V4LCAP__


void *map;

struct image_cap {
  int size;   //Size of the image, in bytes
  int bpp;    //Bits per pixel
  int handle; //File handle for the capture device
  void *data; //image data
};

struct image_cap *Cgrab_image(char* device, int width, int height, 
			      int color, int select_channel);
int Crefresh_image(struct image_cap *image_struct, int width, int height);
int Cfree_image(struct image_cap *image_struct);


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






#endif
