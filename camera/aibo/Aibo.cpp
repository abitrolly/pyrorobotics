#include "Aibo.h"

PyObject *Aibo::updateMMap() {
  // get an image from socket
  /*
        ## Got type=TekkotsuImage
        ## Got format=0
        ## Got compression=1
        ## Got newWidth=104
        ## Got newHeight=80
        ## Got timest=121465
        ## Got frameNum=3185
  */
  char *header;
  header = sock->read(4);  // \r\0\0\0
  printf("read: %d %d %d %d\n", 
	 header[0], 
	 header[1], 
	 header[2], 
	 header[3] );
  
    /*
    type = rawimage_data.readUntil(chr(0)) # "TekkotsuImage"
    print "type:", type
    format = rawimage_data.read()
    print "format:", format
    compression = rawimage_data.read()
    print "compression:", compression
    newWidth = rawimage_data.read()
    print "newWidth:", newWidth
    newHeight = rawimage_data.read()
    print "newHeight:", newHeight
    timeStamp = rawimage_data.read()
    print "timeStamp:", timeStamp
    frameNum = rawimage_data.read()
    print "frameNum:", frameNum
    unknown1 = rawimage_data.read()
    print "unknown1:", unknown1
        ## Got creator=FbkImage
        ## Got chanwidth=104
        ## Got chanheight=80
        ## Got layer=3
        ## Got chan_id=0
        ## Got fmt=JPEGColor
        ## read JPEG: len=2547
    creator = rawimage_data.readUntil(chr(0)) # creator
    print "creator:", creator
    chanWidth = rawimage_data.read()
    print "chanWidth:", chanWidth
    chanHeight = rawimage_data.read()
    print "chanHeight:", chanHeight
    layer = rawimage_data.read()
    print "layer:", layer
    chanID = rawimage_data.read()
    print "chanID:", chanID
    chanWidth = rawimage_data.read()
    print "chanWidth:", chanWidth
    fmt = rawimage_data.readUntil(chr(0)) # fmt
    print "fmt:", fmt
    size = rawimage_data.read()
  */
  return PyInt_FromLong(0L);
}

Aibo::Aibo(char *hostname) {
  // get image details
  sock = new Socket(hostname, 10011);
  width = 100;
  height = 100;
  depth = 3;
  initialize(width, height, depth, 0, 1, 2);
}


