#include <string.h>
#include "blob.h"
#include "hsbrgb.h"
#include <stdio.h>
#include <errno.h>

/* ------------- Blob operations ------------ */

void Blob_init(struct blob* theBlob, struct point* pixel){
  Blob_init_xy(theBlob, pixel->x, pixel->y);
}

void Blob_init_xy(struct blob* theBlob, int x, int y){
  theBlob->mass = 1;
  theBlob->ul.x = theBlob->lr.x = x;
  theBlob->ul.y = theBlob->lr.y = y;
  theBlob->cm_x = (double)x;
  theBlob->cm_y = (double)y;
}

void Blob_addpixel(struct blob* theBlob, struct point* pixel){
  Blob_addpixel_xy(theBlob, pixel->x, pixel->y);
}

void Blob_addpixel_xy(struct blob* theBlob, int x, int y){
  if (x < theBlob->ul.x)
    theBlob->ul.x = x;
  else if (x > theBlob->lr.x)
    theBlob->lr.x = x;
  if (y < theBlob->ul.y)
    theBlob->ul.y = y;
  else if (y > theBlob->lr.y)
    theBlob->lr.y = y;
  theBlob->cm_x = (double)(theBlob->mass * theBlob->cm_x + x)/
    (double)(theBlob->mass + 1);
  theBlob->cm_y = (double)(theBlob->mass * theBlob->cm_y + y)/
    (double)(theBlob->mass + 1);
  theBlob->mass++;
}

void Blob_joinblob(struct blob* theBlob, struct blob* other){
  if (other->ul.x < theBlob->ul.x)
    theBlob->ul.x = other->ul.x;
  else if (other->lr.x > theBlob->lr.x)
    theBlob->lr.x = other->lr.x;
  if (other->ul.y < theBlob->ul.y)
    theBlob->ul.y = other->ul.y;
  else if (other->lr.y > theBlob->lr.y)
    theBlob->lr.y = other->lr.y;
  theBlob->cm_x = (double)(theBlob->mass * theBlob->cm_x + other->mass * other->cm_x) /
    (double)(theBlob->mass + other->mass);
  theBlob->cm_y = (double)(theBlob->mass * theBlob->cm_y + other->mass * other->cm_y) /
    (double)(theBlob->mass + other->mass);
  theBlob->mass += other->mass;
}

/* -------------- Bitmap ops ------------------*/

void Bitmap_init(struct bitmap* map, int w, int h){
  int i;
  map->width = w;
  map->height = h;
  map->data = (uint16_t *) malloc(sizeof(uint16_t) * w*h);
}

void Bitmap_set(struct bitmap* map, int x, int y, uint16_t in){
  if (x >= 0 && x < map->width && y >= 0 && y < map->height){
    map->data[y*map->width + x] = in;
  }
}

uint16_t Bitmap_get(struct bitmap* map, int x, int y){
  if (x >= 0 && x < map->width && y >= 0 && y < map->height){
    return map->data[y*map->width + x];
  }
}

void Bitmap_del(struct bitmap* map){
  free(map->data);
}

/* -------------- Blobdata operations ---------------*/

void Blobdata_init(struct blobdata* data, struct bitmap* theBitmap){
  int count = 0;
  int w, h, n, m, minBlobNum, maxBlobNum, i;
  struct blob* tempBlob;
  data->blobmap = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(data->blobmap, theBitmap->width, theBitmap->height);
  data->equivList = (int *) malloc(sizeof(int) * BLOBLIST_SIZE);
  for (i = 0; i < BLOBLIST_SIZE; i++){
    data->equivList[i] = i;
  }
  data->bloblist = (struct blob**) malloc(sizeof(struct blob*) * BLOBLIST_SIZE);
  memset(data->bloblist, 0,
	 sizeof(struct blob*)*BLOBLIST_SIZE);

  for (w = 0; w < theBitmap->width; w++){
    for (h = 0; h < theBitmap->height; h++){
      if (Bitmap_get(theBitmap, w, h)){
	if (h == 0 && w == 0){
	  tempBlob = (struct blob*) malloc(sizeof(struct blob));
	  Blob_init_xy(tempBlob, w, h);
	  data->bloblist[count] = tempBlob;
	  Bitmap_set(data->blobmap, w, h, count++);
	}
	else if (w == 0){
	  if (Bitmap_get(theBitmap, w, h - 1)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w, h-1)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w, h-1));
	  } else {
	    tempBlob = (struct blob*) malloc(sizeof(struct blob));
	    Blob_init_xy(tempBlob, w, h);
	    data->bloblist[count] = tempBlob;
	    Bitmap_set(data->blobmap, w, h, count++);
	  }
	}
	else if (h == 0){
	  if (Bitmap_get(theBitmap, w-1, h)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w-1, h)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w-1, h));
	  } else {
	    tempBlob = (struct blob*) malloc(sizeof(struct blob));
	    Blob_init_xy(tempBlob, w, h);
	    data->bloblist[count] = tempBlob;
	    Bitmap_set(data->blobmap, w, h, count++);
	  }
	}
	else if (Bitmap_get(theBitmap, w-1, h) &&
		 Bitmap_get(theBitmap, w, h-1)){
	  if (Bitmap_get(data->blobmap, w-1, h) ==
	      Bitmap_get(data->blobmap, w, h-1)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w-1, h)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w-1, h));
	  }
	  else {
	    minBlobNum = min(data->equivList[Bitmap_get(data->blobmap,
								w-1, h)],
			     data->equivList[Bitmap_get(data->blobmap,
								w, h-1)]);
	    maxBlobNum = max(data->equivList[Bitmap_get(data->blobmap,
								w-1, h)],
			     data->equivList[Bitmap_get(data->blobmap,
								w, h-1)]);
	    Blob_addpixel_xy(data->bloblist[minBlobNum], w, h);
	    Bitmap_set(data->blobmap, w, h, minBlobNum);
	    for (n = 0; n < BLOBLIST_SIZE; n++){
	      if (data->equivList[n] == maxBlobNum)
		data->equivList[n] = minBlobNum;
	    }
	  }
	}
	else{
	  if (Bitmap_get(theBitmap, w-1, h)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w-1, h)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w-1, h));
	  }
	  else if (Bitmap_get(theBitmap, w, h-1)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w, h-1)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w, h-1));
	  }
	  else {
	    tempBlob = (struct blob*)malloc(sizeof(struct blob));
	    Blob_init_xy(tempBlob, w, h);
	    data->bloblist[count] = tempBlob;
	    Bitmap_set(data->blobmap, w, h, count++);
	  }
	}
      }
    }
  }

  data->nblobs = 0;
  for (n = 1; n < count; n++){
    if (data->equivList[n] == n){
      for (m = n+1; m < count; m++){
	if (data->equivList[m] == n){
	  Blob_joinblob(data->bloblist[n], data->bloblist[m]);
	  free(data->bloblist[m]);
	  data->bloblist[m] = NULL;
	}
      }
      data->nblobs++;
    }
  }

  for (n = 1; n < count; n++){
    m = n-1;
    while(data->bloblist[m] == NULL){
      data->bloblist[m] = data->bloblist[m+1];
      data->bloblist[m+1] = NULL;
      if (m == 0)
	break;
      m--;
    }
  }
}

void Blobdata_del(struct blobdata* data){
  int i;
  for (i = 0; i < BLOBLIST_SIZE; i++){
    if (data->bloblist[i] != NULL){
      free(data->bloblist[i]);
    }
  }
  free(data->bloblist);
  free(data->equivList);
  Bitmap_del(data->blobmap);
  free(data->blobmap);
}


/* --------------- transducers -----------------
   These functions take image data of some form and reutrn a bitmap
   that can be used with the blob functions.
*/


struct bitmap* bitmap_from_cap(struct image_cap* image, int width, int height){
  int i;
  float h, s, v;
  int red, green, blue;
  struct bitmap* bmp = (struct bitmap*) malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, width, height);
  if (image->bpp == 24){
    for (i = 0; i < image->size; i += 3) {
      red  = ((uint16_t *)image->data)[i + 2];
      green= ((uint16_t *)image->data)[i + 1];
      blue = ((uint16_t *)image->data)[i + 0];
      rmRGBtoHSV(red/255.0,
		 green/255.0,
		 blue/255.0,
		 &h, &s, &v);
      if (v > BITMAP_CUTOFF){
	bmp->data[i/3] = 1;
      }
      else
	bmp->data[i/3] = 0;
    }
  } else if (image->bpp == 8){
    for (i = 0; i < image->size; i++){
      if (((int *)image->data)[i] > (int)BITMAP_CUTOFF*255)
	bmp->data[i] = 1;
      else
	bmp->data[i] = 0;
    }
  }
  return bmp;
}

struct bitmap* bitmap_from_ppm(char* filename){
  int rows, cols, maxval;
  FILE* theFile;
  unsigned char* rgb;
  unsigned int*  RGB;
  struct bitmap* bmp;
  int i, red, green, blue;
  float h, s, v;
  

  theFile = fopen(filename, "r");
  if (!theFile){
    perror("bitmap_from_ppm: Error openeing file for read");
  }
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  fscanf(theFile, "%*2c\n%d %d\n%d", &cols, &rows, &maxval);
  Bitmap_init(bmp, cols, rows);
  if (maxval <= 255){
    rgb = (unsigned char*)malloc(rows*cols*3);
    fread(rgb, 1, rows*cols*3, theFile);
    for (i = 0; i < rows*cols*3; i += 3) {
      red  = rgb[i];
      green= rgb[i + 1];
      blue = rgb[i + 2];
      rmRGBtoHSV(red/(float)maxval,
		 green/(float)maxval,
		 blue/(float)maxval,
		 &h, &s, &v);
      if (v > BITMAP_CUTOFF)
	bmp->data[i/3] = 1;
      else
	bmp->data[i/3] = 0;
    }
    free(rgb);
  }
  else{
    RGB = (unsigned int*)malloc(2*rows*cols*3);
    fread(RGB, 2, rows*cols*3, theFile);
    for (i = 0; i < rows*cols*3; i += 3) {
      red  = RGB[i];
      green= RGB[i + 1];
      blue = RGB[i + 2];
      rmRGBtoHSV(red/(float)maxval,
		 green/(float)maxval,
		 blue/(float)maxval,
		 &h, &s, &v);
      if (v > BITMAP_CUTOFF)
	bmp->data[i/3] = 1;
      else
	bmp->data[i/3] = 0;
    }
    free(RGB);
  }
  fclose(theFile);
  
  return bmp;
}
  
struct bitmap* bitmap_from_pgm(char* filename){
  unsigned int rows, cols, maxval;
  FILE* theFile;
  unsigned char* gray;
  struct bitmap* bmp;
  int i;

  

  theFile = fopen(filename, "r");
  if (!theFile){
    perror("bitmap_from_pgm: Error openeing file for read");
  }


  fscanf(theFile, "%*s%d%d%d", &rows, &cols, &maxval);
  gray = (unsigned char*)malloc(rows*cols);
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, cols, rows);
  fread(gray, 1, rows*cols, theFile);
  fclose(theFile);
  for (i = 0; i < rows*cols; i++) {
    if (gray[i] > BITMAP_CUTOFF)
      bmp->data[i] = 1;
    else
      bmp->data[i] = 0;
  }
  free(gray);
  return bmp;
}


  
/* ------- Blob output ---------
   Given an array of blobdatas, an array of ints, and an int representing the
   length of the previous two arrays (which much be equal), return a struct that looks
   like the player-stage blob struct


struct playerblob* make_player_blob(struct blobdata** blobs, int* channels, int n_channels){
}
*/      
	
	  
  
    
      
