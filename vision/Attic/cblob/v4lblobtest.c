#include "v4lcap.h"
#include "blob.h"
#include <stdio.h>

#define WIDTH 768
#define HEIGHT  480
#define PBMHEADER "P5\n768\n480\n1\n"
#define PGMHEADER_F "P5\n%d\n%d\n%d\n"
#define PPMHEADER "P6\n768\n480\n255\n"

//#define USE_V4L

int main(int argc, char** argv){
  struct image_cap* camera;
  struct bitmap* bmp;
  struct blobdata* thedata;
  FILE* out;
  int i, j;

#ifdef USE_V4L
  camera = Cgrab_image("/dev/video0", WIDTH, HEIGHT, 1, 0);
  printf("Opened device\n");
  printf("bpp: %d\n", camera->bpp);
  Crefresh_image(camera, WIDTH, HEIGHT);
  out = fopen("cap.ppm", "w");
  fprintf(out, PPMHEADER);
  fwrite(camera->data, 1, camera->size, out);
  
  bmp = bitmap_from_cap(camera, WIDTH, HEIGHT);
  printf("Got bitmap_from_cap\n");
#else
  bmp = bitmap_from_ppm("cap.ppm");
  printf("Got bitmap_from_ppm('cap.ppm')\n");
#endif

  out = fopen("bmp.pbm", "w");
  fprintf(out, PBMHEADER);
  printf("Wrote header\n");
  fwrite(bmp->data, 2, bmp->width * bmp->height, out);
  printf("Wrote data\n");
  fclose(out);

  thedata = (struct blobdata*)malloc(sizeof(struct blobdata));
  Blobdata_init(thedata, bmp);
  printf("Blobdata_init\n");

  if (!Bitmap_write_to_pgm(thedata->blobmap, "blob.pgm", thedata->nblobs)){
    printf("Error");
  }
  
  Blobdata_del(thedata);
  free(thedata);
  Bitmap_del(bmp);
  free(bmp);
#ifdef USE_V4L
  Cfree_image(camera);
#endif
  return 0;
}
