/*
  XRCL: The Extensible Robot Control Language
  (c) 2000, Douglas S. Blank
  University of Arkansas, Roboticists Research Group
  http://ai.uark.edu/xrcl/
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
  02111-1307, USA.

  As a special exception, you have permission to link this program
  with the Qt library and distribute executables, as long as you
  follow the requirements of the GNU GPL in regard to all of the
  software in the executable aside from Qt.
*/

/*
 * Adapted from the standard BT848 continuous example for the PXC200 pc104 framegrabber
 *
 *     Needs:
 *       - bt848 driver ver. 011598 by Brad Parker
 *            (ftp://ftp.parker.boston.ma.us/pub/mbone/bt848/bt848-011598.tar.gz)
 *       - bt848-cont.p1 patch by Luca Iocchi
 *            (ftp://ftp.dis.uniroma1.it/~iocchi/Linux/drivers/bt848/bt848-cont.p1)
 */

#include "BT848.h"

BT848::BT848 ( const char* dname, int w, int h ) : Camera(dname, w, h)
{
  bpp = 3;
  size = w * h * 4;
  VIDEO_DEV = devicename;
  ptr = buf = new unsigned char [size + 30/*header*/];
  buffer = new unsigned char [size];
  init();
}

void BT848::Cleanup ()
{
 close (fd);
 delete [] buf;
}

void BT848::GetData ( )
{
  unsigned char *mmptr;
 
  mmptr = grab_one(&cols, &rows);
 
  ptr = buf;
  
  // Put PPM header on buffer
  sprintf ( buf, "P6\n%d %d\n255\n", cols, rows ); 
  
  int pos = strlen(buf);
  rawbuf = buf + pos;

  for (int j=0; j<rows; j++) {
    for (int k=0; k<cols; k++) {
      buf[pos + 2] = *mmptr++;            /* blue */
      buf[pos + 1] = *mmptr++;            /* green */
      buf[pos + 0] = *mmptr++;            /* red */
      *mmptr++;                     /* NULL byte */
      pos += 3;
     }
  }            
  buf_length = pos + rows*cols*3;
}

unsigned char* BT848::grab_one(int *width, int *height) 
{
  /* set input port */
#ifdef USE_SVIDEO_INPUT
  icontrol = METEOR_INPUT_DEV0;        /* PXC200 S-video connector */
#else
  icontrol = METEOR_INPUT_DEV1;        /* PXC200 BNC composite video connector */
#endif
  if (ioctl (fd, METEORSINPUT, &icontrol) < 0) {
    printf ("METEORSINPUT ioctl failed: %d\n", errno);
    exit (1);
  }                          
  /* read the image data */
  if ((icontrol = read (fd, &buffer[0], size)) != size) {
    perror ("read");
    close (fd);
    exit (1);
  }

  /* get error counts */
  if (ioctl (fd, METEORGCOUNT, &cnt)) {
      perror("ioctl GetCount failed");
      exit (1);
  }

  if (0) {
    printf ("Captured:\n  frames: %ld\n  even fields: %ld\n  odd fields: %ld\n",
	    cnt.frames_captured,
	    cnt.even_fields_captured,
	    cnt.odd_fields_captured);
    printf ("Fifo errors: %ld\n", cnt.fifo_errors);
    printf ("DMA errors:  %ld\n", cnt.dma_errors);   
  }
  return buffer;
}

void BT848::init(void) {
  fprintf(stderr,"Init-ing Video under BT848\n");
  struct meteor_geomet geo;
  char rgb[3], header[16], *p;
  int j, k;

  /* open the device */
  if ((fd = open(VIDEO_DEV, O_RDWR)) <= 0) {
    perror (VIDEO_DEV);
    exit (1);
  }

  /* initialize the Imagenation PXC200.
   *
   * WARNING: this function may hang Linux if the board is not a PXC200!!!
   */
  printf ("initializing PXC200\n");
  if (ioctl (fd, BT848_INITPXC200, &icontrol) < 0) {
    perror ("BT848_INITPXC200 ioctl\n");
    exit (1);
  }

  /* set capture geometry */
  geo.rows = rows;              /* # of lines in output image */
  geo.columns = cols;           /* # of pixels in a row in output image */
  geo.frames = 1;               /* # of frames in a buffer */
  geo.oformat = METEOR_GEO_RGB24 ; /* RGB 24 in 4 bytes: NULL,R,G,B */
  if (ioctl (fd, METEORSETGEO, &geo) < 0) {
    perror ("METEORSETGEO ioctl\n");
    exit (1);
  }                             
  /* set input video format */
  icontrol = METEOR_FMT_NTSC;
  if (ioctl (fd, METEORSFMT, &icontrol) < 0) {
    perror ("METEORSFMT ioctl\n");
    exit (1);
  }
}



