#include "v4lcap.h"
#include "blob.h"
#include <stdio.h>


int main(int argc, char** argv){
  struct image_cap* camera;
  struct bitmap* bmp;
  struct blobdata* thedata;
  FILE* out;
  int i, j;
  
  camera = Cgrab_image("/dev/video0", 240, 180, 1, 1);
  
  bmp = bitmap_from_cap(camera, 240, 180);

  Blobdata_init(thedata, bmp);

  out = fopen("blob.pbm", "w");
  fprintf("P5\n240\n180\n1\n", out);
  fwrite(thedata->blobmap->data, 1, 240*180, out);
  fclose(out);
  
  //do stuff

  Blobdata_del(thedata);
  Bitmap_del(bmp);
  Cfree_image(camera);
}
