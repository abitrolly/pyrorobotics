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

#define verbose 1

struct image_cap* Cgrab_image(char* device, int width, int height, int color){
  //struct video_window  vidwin;
  struct video_mbuf    vidmbuf;
  struct video_mmap    vidmmap;
  //struct video_picture vidpict;
  struct image_cap    *image_struct;
  struct video_capability vcap;
  struct video_channel    *vc;
  //char* buf;
  void *image;
  void *map;
  int dev;
  int depth;
  int i;
  int curChannel = 1;

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

  // ----------------------------------------------------------------
  // Additional hints from Swarthmore's Vision Module
  // by Bruce Maxwell
  // ----------------------------------------------------------------

  /* queries the video device to find out its capabilities
      - name
      - type
      - channels
      - audios
      - maxwidth
      - maxheight
      - minwidth
      - minheight
  */
  if(ioctl(dev, VIDIOCGCAP, &vcap)<0){
    perror("VIDIOCGCAP");
    exit(-1);
  }
 
  if (verbose) {
    fprintf(stderr,"Video Capture Device Name : %s\n",
            vcap.name);
    fprintf(stderr,"Maximum size (w, h): (%d, %d)\n",
            vcap.maxwidth,
            vcap.maxheight);
    fprintf(stderr,"Minimum size (w, h): (%d, %d)\n",
            vcap.minwidth,
            vcap.minheight);
  }
                                                                                  /* queries the video device for the channel information
     - channel
     - name
     - tuners
     - flags (channel has a tuner (1), channel has audio (2))
     - type (tv (1), camera (2))
     - norm (set by channel)
  */
  vc = (struct video_channel *)malloc(sizeof(struct video_channel) * vcap.channels);
  if(vc == NULL) {
    fprintf(stderr, "OpenVideoDevice: Unable to allocate memory\n");
    return(NULL);
  }

  for (i=0; i < vcap.channels; i++){
    vc[i].channel = i;
    if(ioctl(dev, VIDIOCGCHAN, &(vc[i]))<0){
      perror("VIDIOCGCHAN");
      exit(-1);
    }
    
    if (verbose) {
      fprintf(stderr,"Video Source (%d) Name : %s\n",i, vc[i].name);
      fprintf(stderr, "Flags %d, type %d, norm %d\n",
              (int)vc[i].flags,
              (int)vc[i].type,
              (int)vc[i].norm);
    }
  }

  // ----------------------------------------------------------------
  // End of hints from SVM
  // ----------------------------------------------------------------

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

  vc[curChannel].channel = 1;
  vc[curChannel].norm = 1; // this seems to be necessary (?)
  if(ioctl(dev, VIDIOCSCHAN, &(vc[curChannel])) < 0){
    perror("VIDIOCSCHAN");
    munmap(map, vidmbuf.size);
    return(NULL);
  }
  //Start caputring
  if (ioctl(dev, VIDIOCMCAPTURE, &vidmmap)){
    perror("Cgrab_image, ioctl CMCAPTURE");
    munmap(map, vidmbuf.size);
    close(dev);
    free(image_struct);
    return NULL;
  }
  if (ioctl(dev, VIDIOCSYNC, &vidmmap)){
    perror("Cgrab_image, ioctl CSYNC");
    munmap(map, vidmbuf.size);
    close(dev);
    free(image_struct);
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
#define PGM_HEADER "P6\n384 240\n65536\n"

int main(void){
  struct image_cap *image;
  struct video_capability vcap;
  int savefile;
  int testhandle;

  testhandle = open("/dev/video0", O_RDWR);
  if (testhandle < 0){
    perror("Error opening");
    return 1;
  }

  if (ioctl (testhandle, VIDIOCGCAP, &vcap)) {
    perror ("ioctl error");
    close(testhandle);
    return 1;
  }
  close(testhandle);

  

  printf("Starting test...\n");

  image = Cgrab_image("/dev/video0", 384, 240, 1);
  printf("Handle: %d\n", image->handle);

  printf("called Cgrab_image\n");

  savefile = open("./vcap.ppm", O_CREAT | O_WRONLY, S_IRWXU);
  if (savefile < 0){
    perror("Opening savefile");
    Cfree_image(image);
    exit(1);
  }

  write(savefile, PGM_HEADER, strlen(PGM_HEADER));
  write(savefile, image->data, image->size);

  close(savefile);


  if (testhandle < 0){
    perror("Error opening again");
    return 1;
  }
  image->handle = testhandle;

  if (Cfree_image(image)){
    printf("Error in Cfree_image\n");
    return 1;
  }
  printf("Called Cfree_image\n");

  image = Cgrab_image("/dev/video0", 384, 240, 1);
  if (image == NULL){
    printf("Error in Cgrab_image(2)\n");
    return 1;
  }
  printf("Called Cgrab_image(2)\n");
  
  if (Crefresh_image(image, 384, 240)){
    printf("Error in Crefresh_image\n");
    return 1;
  }
	   
  printf("Called Crefresh_image(2)\n");

  if (Cfree_image(image)){
    printf("Error in Cfree_image(2)\n");
    return 1;
  }
  printf("Called Cfree_image(2)\n");

  return 0;
}

#endif

