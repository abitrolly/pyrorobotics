#ifndef __V4LCAP__
#define __V4LCAP__

struct image_cap {
  int size;   //Size of the image, in bytes
  int bpp;    //Bits per pixel
  void *data; //image data
};

struct image_cap * Cgrab_image(char* device, int width, int height);

#endif
