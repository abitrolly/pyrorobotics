#include <stdlib.h>
#include <stdio.h>
#include <linux/videodev.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <error.h>
#include <unistd.h>
#include <string.h>

#include "v4lcap.h"

struct image_cap* Cgrab_image(char* device, int width, int height, int color){
  //struct video_window  vidwin;
  struct video_mbuf    vidmbuf;
  struct video_mmap    vidmmap;
  //struct video_picture vidpict;
  struct image_cap    *image_struct;
  //char* buf;
  void *image;
  void *map;
  int dev;
  int depth;

  image_struct = malloc(sizeof(struct image_cap));
  if (image_struct == NULL){
    perror("Cgrab_image, struct image_struct malloc()");
    return NULL;
  }

  //open the video device file
  dev = open(device, O_RDWR);
  if (dev < 0){
    perror("Cgrab_image, device Open error");
    return NULL;
  }

  //Request Memory map
  if (ioctl (dev, VIDIOCGMBUF, &vidmbuf)) {
    perror ("Cgrab_image, ioctl (VIDIOCGMBUF)");
    close(dev);
    return NULL;
  }

  //create mmap
  map = mmap(0, vidmbuf.size, PROT_READ | PROT_WRITE, MAP_SHARED, dev, 0);
  if ((unsigned char *)-1 == (unsigned char *)map) {
    perror ("Cgrab_image, mmap()");
    close(dev);
    return NULL;
  }


  switch (color){
  case 0: //No color
    vidmmap.format = VIDEO_PALETTE_GREY;
    depth = 1;
    break;
  default:
    vidmmap.format = VIDEO_PALETTE_RGB24;
    depth = 3;
  }

  vidmmap.frame  = 0;
  vidmmap.width  = width;
  vidmmap.height = height;
  image_struct->size = height * width * depth;

  /*if ((image = malloc(image_struct->size)) == NULL){
    perror("image malloc()");
    close(dev);
    return NULL;
    }*/

  //Start caputring
  if (ioctl(dev, VIDIOCMCAPTURE, &vidmmap)){
    perror("Cgrab_image, ioctl CMCAPTURE");
    close(dev);
    free(image);
    return NULL;
  }

  if (ioctl(dev, VIDIOCSYNC, &vidmmap)){
    perror("Cgrab_image, ioctl CSYNC");
    close(dev);
    free(image);
    return NULL;
  }
    

  image_struct->data = map;
  image_struct->bpp  = depth * 8;
  image_struct->handle = dev;

  return image_struct;
}

int Crefresh_image(struct image_cap *image_struct, int width, int height){
  struct video_mmap vidmmap;

  switch (image_struct->bpp){
  case 8:
    vidmmap.format = VIDEO_PALETTE_GREY;
    break;
  case 24:
    vidmmap.format = VIDEO_PALETTE_RGB24;
    break;
  default:
    perror("Crefresh_image, invalid bpp");
    return -1;
  }
  vidmmap.frame = 0;
  vidmmap.width = width;
  vidmmap.height = height;

  if (ioctl(image_struct->handle, VIDIOCMCAPTURE, &vidmmap)){
    perror("Crefresh_image, ioctl MCAPTURE");
    return -1;
  }

  //Sync with the capture device
  if (ioctl(image_struct->handle, VIDIOCSYNC, &vidmmap)){
    perror("Crefresh_image, ioctl CSYNC");
    return -1;
  }
  
  return 0;
}
  
//Release the mmap
int Cfree_image(struct image_cap *image_struct){
  //Unmap the mapped memory
  if (munmap(image_struct->data, image_struct->size)){
    perror("Cfree_image, munmap");
    return -1;
  }

  if (close(image_struct->handle)){
    perror("Cfree_image, close device");
    return -1;
  }
  
  free(image_struct);

  return 0;
}

#ifdef DEBUG__
#define PGM_HEADER "P6\n384 240\n65535\n"

int main(void){
  struct image_cap *image;
  int savefile;

  printf("Starting test...");

  image = Cgrab_image("/dev/video0", 384, 240);

  printf("called Cgrab_image");

  savefile = open("./vcap.ppm", O_CREAT | O_WRONLY, S_IRWXU);
  if (savefile < 0){
    perror("Opening savefile");
    free(image);
    exit(1);
  }

  write(savefile, PGM_HEADER, strlen(PGM_HEADER));
  write(savefile, image->data, image->size);

  close(savefile);

  free(image->data);
  free(image);

  return 0;
}

#endif

