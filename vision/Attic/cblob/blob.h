#ifndef __BLOB_H__
#define __BLOB_H__

#include "v4lcap.h"

#define BLOBLIST_SIZE 2000
#define BITMAP_CUTOFF 0.5
#define min(X, Y)  ((X) < (Y) ? (X) : (Y))
#define max(X, Y)  ((X) > (Y) ? (X) : (Y))

//Given a bitmap, computes an (x,y) offset (row-major)
//#define bm_offset(bm, x, y)  x*bm->width + y


struct point{
  int x;
  int y;
};

struct bitmap{
  int width;
  int height;
  unsigned char* data;
};

struct blob{
  int mass;
  struct point ul;
  struct point lr;
  double cm_x;
  double cm_y;
};

struct blobdata{
  int width;
  int height;
  int nblobs;
  struct bitmap* blobmap;
  int* equivList;
  struct blob** bloblist;
};

struct playerblob{
  //more to come.
};
  

void Blob_init(struct blob* theBlob, struct point* pixel);
void Blob_init_xy(struct blob* theBlob, int x, int y); 
void Blob_addpixel(struct blob* theBlob, struct point* pixel);
void Blob_addpixel_xy(struct blob* theBlob, int x, int y);
void Blob_joinblob(struct blob* theBlob, struct blob* other);

void Bitmap_init(struct bitmap* map, int w, int h);
void Bitmap_set(struct bitmap* map, int x, int y, unsigned char in);
unsigned char Bitmap_get(struct bitmap* map, int x, int y);
void Bitmap_del(struct bitmap* map);
  
void Blobdata_init(struct blobdata* data, struct bitmap* theBitmap);
void Blobdata_del(struct blobdata* data);

struct bitmap* bitmap_from_cap(struct image_cap* image, int width, int height);

  //struct playerblob* make_player_blob(struct blobdata** blobs, int* channels, int n_channels);

#endif
