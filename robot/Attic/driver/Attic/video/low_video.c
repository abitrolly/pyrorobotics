#include<errno.h>
#include<string.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include<stdio.h>

#include<linux/videodev.h>
#include"low_video.h"

int setPrefs(int fd, int xres, int yres){
  int err;
  struct video_window win;

  err = ioctl(fd,VIDIOCGWIN,&win);
  if(err == -1){
    fprintf(stderr,"Video cannot read video properties from video device: %s\n",strerror(errno));
    return errno;
  }
  
  win.width = xres;
  win.height= yres;
  win.clips = NULL;
  win.clipcount = 0;
  win.flags = VIDEO_CAPTURE_ODD;

  err = ioctl(fd,VIDIOCSWIN,&win);
  if(err == -1){
    fprintf(stderr,"Video cannot read video properties from video device: %s\n",strerror(errno));
    return errno;
  }
  
  return 0;
}
