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


struct image_cap* Cgrab_image(char* device, int width, int height){
  //struct video_window  vidwin;
  struct video_mbuf    vidmbuf;
  struct video_mmap    vidmmap;
  //struct video_picture vidpict;
  struct image_cap    *image_struct;
  //char* buf;
  void *image;
  char *map;
  int dev;

  image_struct = malloc(sizeof(struct image_cap));
  if (image_struct == NULL){
    perror("struct image_struct malloc()");
    return NULL;
  }

  //open the video device file
  dev = open(device, O_RDWR);
  if (dev < 0){
    perror("Open error");
    return NULL;
  }

  //Request Memory map
  if (ioctl (dev, VIDIOCGMBUF, &vidmbuf)) {
    perror ("ioctl (VIDIOCGMBUF)");
    close(dev);
    return NULL;
  }

  //create mmap
  map = mmap(0, vidmbuf.size, PROT_READ | PROT_WRITE, MAP_SHARED, dev, 0);
  if ((unsigned char *)-1 == (unsigned char *)map) {
    perror ("mmap()");
    close(dev);
    return NULL;
  }


  

  //Fill video_mmap struct
  vidmmap.format = VIDEO_PALETTE_RGB24;
  vidmmap.frame  = 0;
  vidmmap.width  = width;
  vidmmap.height = height;
  image_struct->size = height * width * 3;

  if ((image = malloc(image_struct->size)) == NULL){
    perror("image malloc()");
    close(dev);
    return NULL;
  }

  //Start caputring
  if (ioctl(dev, VIDIOCMCAPTURE, &vidmmap)){
    perror("CMCAPTURE");
    close(dev);
    free(image);
    exit(1);
  }

  //Sync with the capture device
  if (ioctl(dev, VIDIOCSYNC, &vidmmap)){
    perror("CSYNC");
    close(dev);
    free(image);
    exit(1);
  }

  //Copy image from the mmap to image
  memcpy(image, map, image_struct->size);

  image_struct->data = image;
  image_struct->bpp  = 32;

  close(dev);

  //Unmap the memory, ending capture
  if (munmap(map, image_struct->size) < 0){
    perror("munmap");
    return NULL;
  }
  
  return image_struct;
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

