#ifndef __V4LCAP__
#define __V4LCAP__

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

#endif
