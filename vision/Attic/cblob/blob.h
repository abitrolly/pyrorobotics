#ifndef __BLOB_H__
#define __BLOB_H__

#include "v4lcap.h"
#include <stdint.h>
#include <player.h>

#define BLOBLIST_SIZE 10000
#define BITMAP_CUTOFF 0.5
#define PLAYERBLOB_MAX_CHANNELS 8
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
  uint16_t* data;
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

typedef struct player_blobfinder_data_varsize{
  uint16_t width, height;
  int n_channels;
  player_blobfinder_header_elt_t* header;
  player_blobfinder_blob_elt_t* blobs;
} playerblob_t;


void Blob_init(struct blob* theBlob, struct point* pixel);
void Blob_init_xy(struct blob* theBlob, int x, int y); 
void Blob_addpixel(struct blob* theBlob, struct point* pixel);
void Blob_addpixel_xy(struct blob* theBlob, int x, int y);
void Blob_joinblob(struct blob* theBlob, struct blob* other);

void Bitmap_init(struct bitmap* map, int w, int h);
void Bitmap_set(struct bitmap* map, int x, int y, uint16_t in);
uint16_t Bitmap_get(struct bitmap* map, int x, int y);
void Bitmap_del(struct bitmap* map);
int Bitmap_write_to_pgm(struct bitmap* map, char* filename, int levels);
  
void Blobdata_init(struct blobdata* data, struct bitmap* theBitmap);
void Blobdata_del(struct blobdata* data);

struct bitmap* bitmap_from_cap(struct image_cap* image, int width, int height);
struct bitmap* bitmap_from_ppm(char* filename);
struct bitmap* bitmap_from_pgm(char* filename);

player_blobfinder_data_t* make_player_blob(struct blobdata** blobs, uint32_t* channels, int n_channels);
playerblob_t* make_player_blob_varsize(struct blobdata** blobs, uint32_t* channels, int n_channels);
void playerblob_del(playerblob_t* blobs);

#endif
