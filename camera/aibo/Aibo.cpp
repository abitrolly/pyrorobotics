#include "Aibo.h"

long convert(char *buff) {
  long retval = 0;
  retval += (buff[0] <<  0);
  retval += (buff[1] <<  8);
  retval += (buff[2] << 16);
  retval += (buff[3] << 24);
  return retval;
}

PyObject *Aibo::updateMMap() {
  char *header, *type, *creator, *fmt, *image;
  long format, compression, newWidth, newHeight, timeStamp, frameNum, unknown1;
  long chanWidth, chanHeight, layer, chanID, unknown2, size;
  // get an image from socket
  // Got type=TekkotsuImage
  // Got format=0
  // Got compression=1
  // Got newWidth=104
  // Got newHeight=80
  // Got timest=121465
  // Got frameNum=3185
  header = sock->read(4);  // \r\0\0\0
  type = sock->readUntil((char)0); // "TekkotsuImage"
  printf("type: %s\n", type);
  format = convert(sock->read(4));
  printf("format: %ld\n", format);
  compression = convert(sock->read(4));
  printf("compression: %ld\n", compression);
  newWidth = convert(sock->read(4));
  printf("newWidth: %ld\n", newWidth);
  newHeight = convert(sock->read(4));
  printf("newHeight: %ld\n", newHeight);
  timeStamp = convert(sock->read(4));
  printf("timeStamp: %ld\n", timeStamp);
  frameNum = convert(sock->read(4));
  printf("frameNum: %ld\n", frameNum);
  unknown1 = convert(sock->read(4));
  printf("unknown1: %ld\n", unknown1);
  //// Got creator=FbkImage
  //// Got chanwidth=104
  //// Got chanheight=80
  //// Got layer=3
  //// Got chan_id=0
  //// Got fmt=JPEGColor
  //// read JPEG: len=2547
  creator = sock->readUntil((char)0); // creator
  printf("creator: %s\n", creator);
  chanWidth = convert(sock->read(4));
  printf("chanWidth: %ld\n", chanWidth);
  chanHeight = convert(sock->read(4));
  printf("chanHeight: %ld\n", chanHeight);
  layer = convert(sock->read(4));
  printf("layer: %ld\n", layer);
  chanID = convert(sock->read(4));
  printf("chanID: %ld\n", chanID);
  unknown2 = convert(sock->read(4));
  printf("unknown2: %ld\n", unknown2);
  fmt = sock->readUntil((char)0); // fmt
  printf("fmt: %s\n", fmt);
  size = convert(sock->read(4));
  image = sock->read(size);
  // convert image from JPEG to RGB in mmap
  return PyInt_FromLong(size);
}

Aibo::Aibo(char *hostname) {
  // get image details
  sock = new Socket(hostname, 10011);
  width = 100;
  height = 100;
  depth = 3;
  initialize(width, height, depth, 0, 1, 2);
}

