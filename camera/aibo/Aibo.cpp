#include "Aibo.h"

#include "jpeglib.h"

long convert(char *buff) {
  long retval = 0;
  retval += (buff[0] <<  0);
  retval += (buff[1] <<  8);
  retval += (buff[2] << 16);
  retval += (buff[3] << 24);
  return retval;
}

static void init_source (j_decompress_ptr cinfo) {
  // nothing
}
static boolean fill_input_buffer (j_decompress_ptr cinfo) {
  struct jpeg_source_mgr *src = cinfo->src;
  // WARNMS(cinfo, JWRN_JPEG_EOF);
  /* Insert a fake EOI marker */
  char buffer[2] = { (JOCTET) 0xFF, (JOCTET) JPEG_EOI };
  // The next two lines were READ ONLY?
  //src->next_input_byte[0] = (JOCTET) 0xFF;
  //src->next_input_byte[1] = (JOCTET) JPEG_EOI;
  memcpy((void *)src->next_input_byte, buffer, 2);
  src->bytes_in_buffer = 2;
  return TRUE;
}
static void skip_input_data (j_decompress_ptr cinfo, long num_bytes) {
  struct jpeg_source_mgr *src = cinfo->src;
  if (num_bytes > 0) {
    while (num_bytes > (long) src->bytes_in_buffer) {
      num_bytes -= (long) src->bytes_in_buffer;
      (void) fill_input_buffer(cinfo);
      /* note we assume that fill_input_buffer will never return FALSE,
       * so suspension need not be handled.
       */
    }
    src->next_input_byte += (size_t) num_bytes;
    src->bytes_in_buffer -= (size_t) num_bytes;
  }
}
static void resync_to_restart (j_decompress_ptr cinfo, int desired) {
  // nothing
}
static void term_source (j_decompress_ptr cinfo) {
  // nothing
}
static void jpeg_memory_src (j_decompress_ptr cinfo, 
			     void* buffer, unsigned int nbyte) {
  struct jpeg_source_mgr *src;
  if (cinfo->src == NULL) {/* first time for this JPEG object? */
    cinfo->src = (struct jpeg_source_mgr *)
      (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_PERMANENT,
  				  sizeof(struct jpeg_source_mgr));
  }
  src = cinfo->src;
  src->next_input_byte = (JOCTET *)
    (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_PERMANENT,
  				nbyte * sizeof(JOCTET));
  src->init_source = init_source;
  src->fill_input_buffer = fill_input_buffer;
  src->skip_input_data = skip_input_data;
  src->resync_to_restart = jpeg_resync_to_restart; /* use default method */
  src->term_source = term_source;
  src->bytes_in_buffer = nbyte; /* forces fill_input_buffer on first read */
  memcpy((void *)src->next_input_byte, buffer, nbyte);
}

int jpeg_decompress(char *image_buffer, unsigned int size) {
  // URL: http://courses.cs.deu.edu.tr/cse566/newpage2.htm
  /* This struct contains the JPEG decompression parameters and pointers to
   * working space (which is allocated as needed by the JPEG library).
   */
  struct jpeg_decompress_struct cinfo;
  JSAMPARRAY buffer;/* Output row buffer */
  int row_stride;/* physical row width in output buffer */

  /* Step 1: allocate and initialize JPEG decompression object */
  jpeg_create_decompress(&cinfo);

  /* Step 2: specify data source (eg, a file) */
  // jpeg_stdio_src(&cinfo, infile); // file
  jpeg_memory_src(&cinfo, image_buffer, size); // memory

  /* Step 3: read file parameters with jpeg_read_header() */
  (void) jpeg_read_header(&cinfo, TRUE);
  /* We can ignore the return value from jpeg_read_header since
   *   (a) suspension is not possible with the stdio data source, and
   *   (b) we passed TRUE to reject a tables-only JPEG file as an error.
   * See libjpeg.doc for more info.
   */

  /* Step 4: set parameters for decompression */

  /* In this example, we don't need to change any of the defaults set by
   * jpeg_read_header(), so we do nothing here.
   */

  /* Step 5: Start decompressor */

  (void) jpeg_start_decompress(&cinfo);
  /* We can ignore the return value since suspension is not possible
   * with the stdio data source.
   */

  /* We may need to do some setup of our own at this point before reading
   * the data.  After jpeg_start_decompress() we have the correct scaled
   * output image dimensions available, as well as the output colormap
   * if we asked for color quantization.
   * In this example, we need to make an output work buffer of the right size.
   */ 
  /* JSAMPLEs per row in output buffer */
  row_stride = cinfo.output_width * cinfo.output_components;
  /* Make a one-row-high sample array that will go away when done with image */
  buffer = (*cinfo.mem->alloc_sarray)
    ((j_common_ptr) &cinfo, JPOOL_IMAGE, row_stride, 1);

  /* Step 6: while (scan lines remain to be read) */
  /*           jpeg_read_scanlines(...); */

  /* Here we use the library's state variable cinfo.output_scanline as the
   * loop counter, so that we don't have to keep track ourselves.
   */
  while (cinfo.output_scanline < cinfo.output_height) {
    /* jpeg_read_scanlines expects an array of pointers to scanlines.
     * Here the array is only one element long, but you could ask for
     * more than one scanline at a time if that's more convenient.
     */
    (void) jpeg_read_scanlines(&cinfo, buffer, 1);
    /* Assume put_scanline_someplace wants a pointer and sample count. */
    //put_scanline_someplace(buffer[0], row_stride); FIX
    // MAYBE THIS IS WHERE WE CAN GET X,Y
    // buffer[0] should be rgb * width, I think
  }

  /* Step 7: Finish decompression */

  (void) jpeg_finish_decompress(&cinfo);
  /* We can ignore the return value since suspension is not possible
   * with the stdio data source.
   */

  /* Step 8: Release JPEG decompression object */

  /* This is an important step since it will release a good deal of memory. */

  jpeg_destroy_decompress(&cinfo);
  return 1;
}

PyObject *Aibo::updateMMap() {
  char *header, *type, *creator, *fmt, *image_buffer;
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
  image_buffer = sock->read(size);
  // convert image from JPEG to RGB in mmap
  if (width == 0 && height == 0) {
    width = newWidth;
    height = newHeight;
    printf("New image size: %d x %d; %ld\n", width, height, size);
    return PyInt_FromLong(0);
  }
  if (size > 0 && size < 10000) {
    jpeg_decompress(image_buffer, (unsigned int) size);
    return PyInt_FromLong(size);
  } else {
    printf("Aibo camera bad JPEG size: %ld\n", size);
  }
  return PyInt_FromLong(0);
}

Aibo::Aibo(char *hostname) {
  // get image details
  sock = new Socket(hostname, 10011);
  depth = 3;
  // set width, height 0 to trigger automatically:
  width = 0;
  height = 0;
  updateMMap(); // this will set height and width automatically
  initialize(width, height, depth, 0, 1, 2); // create some space
}

/*
From: /usr/share/doc/libjpeg-devel-6b/libjpeg.doc
A data source manager provides five methods:

init_source (j_decompress_ptr cinfo)
        Initialize source.  This is called by jpeg_read_header() before any
        data is actually read.  Unlike init_destination(), it may leave
        bytes_in_buffer set to 0 (in which case a fill_input_buffer() call
        will occur immediately).

fill_input_buffer (j_decompress_ptr cinfo)
        This is called whenever bytes_in_buffer has reached zero and more
        data is wanted.  In typical applications, it should read fresh data
        into the buffer (ignoring the current state of next_input_byte and
        bytes_in_buffer), reset the pointer & count to the start of the
        buffer, and return TRUE indicating that the buffer has been reloaded.
        It is not necessary to fill the buffer entirely, only to obtain at
        least one more byte.  bytes_in_buffer MUST be set to a positive value
        if TRUE is returned.  A FALSE return should only be used when I/O
        suspension is desired (this mode is discussed in the next section).

skip_input_data (j_decompress_ptr cinfo, long num_bytes)
        Skip num_bytes worth of data.  The buffer pointer and count should
        be advanced over num_bytes input bytes, refilling the buffer as
        needed.  This is used to skip over a potentially large amount of
        uninteresting data (such as an APPn marker).  In some applications
        it may be possible to optimize away the reading of the skipped data,
        but it's not clear that being smart is worth much trouble; large
        skips are uncommon.  bytes_in_buffer may be zero on return.
        A zero or negative skip count should be treated as a no-op.

resync_to_restart (j_decompress_ptr cinfo, int desired)
        This routine is called only when the decompressor has failed to find
        a restart (RSTn) marker where one is expected.  Its mission is to
        find a suitable point for resuming decompression.  For most
        applications, we recommend that you just use the default resync
        procedure, jpeg_resync_to_restart().  However, if you are able to back
        up in the input data stream, or if you have a-priori knowledge about
        the likely location of restart markers, you may be able to do better.
        Read the read_restart_marker() and jpeg_resync_to_restart() routines
        in jdmarker.c if you think you'd like to implement your own resync
        procedure.

term_source (j_decompress_ptr cinfo)
        Terminate source --- called by jpeg_finish_decompress() after all
        data has been read.  Often a no-op.

*/
