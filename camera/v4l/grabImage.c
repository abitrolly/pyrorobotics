#include <Python.h>
#include "v4lcap.h"
#include <time.h>

#define BLUE     0
#define GREEN    1
#define RED      2
#define MAXBLOBS 2000

/*********
 * Arguments: (string device_name,
 *             int width,
 *             int height
 *             int color)
 *
 *   Color is a true/false value.  For now, if color is true,
 *    the image will be in 24 bpp color, and if it's false, it
 *    will be in 8 bpp greyscale.
 *
 * Returns: (int size, int bpp, int handle, buffer data)
 *          handle is the file handle for the image capture
 *          device, and it needs to get passed back to the
 *          C level for refresh and free operations.
 *********/
 
static PyObject *grab_image(PyObject *self, PyObject *args){
  char *device;
  int width, height, color, channel;
  struct image_cap *image;
  PyObject *buffer, *tuple;

  //Expects grab_image(device_name, width, height, color, channel)
  if(!PyArg_ParseTuple(args, "siiii", &device, &width, &height, &color, &channel)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to grab_image");
    return NULL;
  }

  image = Cgrab_image(device, width, height, color, channel);
  if (image == NULL){
    PyErr_SetString(PyExc_IOError, "Error in C function call");
    return NULL;
  }

  buffer = PyBuffer_FromMemory(image->data, image->size);

  tuple = Py_BuildValue("iiiO", image->size, image->bpp, image->handle, buffer);

  free(image);

  return tuple;
}

//Free the buffer given by grab_image
//Expects free_image(handle, buffer)
//Returns 0 for success
static PyObject *free_image(PyObject *self, PyObject *args){
  PyObject *obj, *buffer;
  int dev;
  struct image_cap *image_struct;

  //Get the buffer object from the arguments
  if (!PyArg_ParseTuple(args, "iO", &dev, &obj)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to free_image");
    return NULL;
  }

  //Make sure it's a valid buffer object
  if (!PyBuffer_Check(obj)){
    PyErr_SetString(PyExc_TypeError, "Invalid argument: not a PyBuffer");
    return NULL;
  }

  //Convert the object to a buffer object
  buffer = PyBuffer_FromObject(obj, 0, Py_END_OF_BUFFER);

  //This shouldn't be an error if the object passes the previous check
  if (buffer->ob_type->tp_as_buffer->bf_getreadbuffer == NULL){
    PyErr_SetString(PyExc_TypeError, "Invalid argument: not a readable PyBuffer");
    return NULL;
  }

  //Create an image_cap structure
  image_struct = malloc(sizeof(struct image_cap));

  //This call puts the size of PyBuffer object into image_struct.size
  //and sets the image_struct->data pointer to the beginning of the
  //PyBuffer's buffer
  image_struct->size = (int)(buffer->ob_type->tp_as_buffer->bf_getreadbuffer)\
                           (buffer, 0, &(image_struct->data));
  image_struct->handle = dev;
  
  if (Cfree_image(image_struct)){
    free(image_struct);
    PyErr_SetString(PyExc_IOError, "Error in C function call");
    return NULL;
  }
  
  return PyInt_FromLong(0L);
}

//Expects (int handle, int width, int height, int depth)
//Returns 0 upon success
static PyObject *refresh_image(PyObject *self, PyObject *args){
  int dev, w, h, d;
  struct image_cap image_struct;

  if(!PyArg_ParseTuple(args, "iiii", &dev, &w, &h, &d)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to free_image");
    return NULL;
  }

  image_struct.handle = dev;
  image_struct.bpp = d;
  
  if(Crefresh_image(&image_struct, w, h)){
    PyErr_SetString(PyExc_IOError, "Error in C function call");
    return NULL;
  }

  return PyInt_FromLong(0L);
}



static PyObject *super_red(PyObject *self, PyObject *args)
{
  int w, h;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "ii", &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_red");
    return NULL;
  }

  p=map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = *(p+2) - (*(p+1) + *p);
      if (temp<0)
	*(p+2) = 0;
      else
	*(p+2) = 255;
      *(p+1) = 0;
      *p = 0;
      p += 3;
    }
  }

  return PyInt_FromLong(0L);
}  

static PyObject *super_blue(PyObject *self, PyObject *args)
{
  int w, h;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "ii", &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_blue");
    return NULL;
  }

  p=map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = *p - (*(p+1) + *(p+2));
      if (temp<0)
	*p = 0;
      else
	*p = temp;
      *(p+1) = 0;
      *(p+2) = 0;
      p += 3;
    }
  }

  return PyInt_FromLong(0L);
}  

static PyObject *super_green(PyObject *self, PyObject *args)
{
  int w, h;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "ii", &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_green");
    return NULL;
  }

  p=map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = *(p+1) - (*p + *(p+2));
      if (temp<0)
	*(p+1) = 0;
      else
	*(p+1) = temp;
      *p = 0;
      *(p+2) = 0;
      p += 3;
    }
  }

  return PyInt_FromLong(0L);
}  

static PyObject *super_yellow(PyObject *self, PyObject *args)
{
  int w, h;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "ii", &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_yellow");
    return NULL;
  }

  p=map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      /*      temp = *(p+1) - (*p + *(p+2));*/
      temp = *(p+1) - *p;
      if (temp<0)
	*(p+1) = 0;
      else
	*(p+1) = temp;
      *p = 0;
      *(p+2) = 0;
      p += 3;
    }
  }
  
  return PyInt_FromLong(0L);
}  

static PyObject *super_white(PyObject *self, PyObject *args)
{
  int w, h;
  int i, j, temp;
  unsigned char *p;
  
  if(!PyArg_ParseTuple(args, "ii", &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_white");
    return NULL;
  }
  
  p=map;
  
  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      if (!((*p > 240) && (*(p+1)>240) && (*(p+2)>240)))
	{
	  *p = 0; *(p+1) = 0; *(p+2) = 0;
	}
      p += 3;
    }
  }
  
  return PyInt_FromLong(0L);
}  

static PyObject *super_color(PyObject *self, PyObject *args)
{
  int keep_red, keep_green, keep_blue, channel, w, h;
  int i, j, temp, max, a, b, c;
  float red_mult, green_mult, blue_mult;
  unsigned char *p;
  
  if(!PyArg_ParseTuple(args, "iiiiii", &keep_red, 
		       &keep_green, &keep_blue, &channel, &w, &h))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_color");
      return NULL;
    }
  
  p=map;
  
  /* find max channel -- that's the one that will be subtracted from*/
  if ((keep_red>=keep_green) && (keep_red>=keep_blue))
    {
      red_mult = ((float)keep_red)/100.0;
      green_mult = -(100.0-((float)keep_green))/100.0;
      blue_mult = -(100.0-((float)keep_blue))/100.0;
    }
  else if ((keep_green>=keep_red) && (keep_green>=keep_blue))
    {
      red_mult = -(100.0-(float)keep_red)/100.0;
      green_mult = ((float)keep_green)/100.0;
      blue_mult = -(100.0-((float)keep_blue))/100.0;
    }
  else
    {
      red_mult = -(100.0-((float)keep_red))/100.0;
      green_mult = -(100.0-((float)keep_green))/100.0;
      blue_mult = ((float)keep_blue)/100.0;
    }

  /* a, b, and c are offsets for pointer arithmetic */
  if (channel == RED)
    {
      a=2; b=0; c=1;
    }
  else if (channel == GREEN)
    {
      a=1; b=0; c=2;
    }
  else /*channel == BLUE */
    {
      a=0; b=1; c=2;
    }

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = (int)(*(p+2)*red_mult + *(p+1)*green_mult + *p*blue_mult);

      /* Floor of temp is 0 */
      if (temp<0) temp =0;
      
      *(p+a) = temp;
      *(p+b) = 0;
      *(p+c) = 0;

      p += 3;
    }
  }

  return PyInt_FromLong(0L);
}  

static PyObject *color_filter(PyObject *self, PyObject *args)
{
  int lr,lg,lb;
  int hr,hg,hb;
  int channel,width,height;
  int w,h,offset,m1,m2;

  unsigned char *image;
  
  
  if(!PyArg_ParseTuple(args, "iiiiiiiii", &lr,&lg,&lb,&hr,&hg,&hb,
		       &channel, &width, &height))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to color_filter");
      return NULL;
    }
  
  /* offset, m1, and m2 are offsets for pointer arithmetic */
  if (channel == RED)
    {
      offset=2; m1=0; m2=1;
    }
  else if (channel == GREEN)
    {
      offset=1; m1=0; m2=2;
    }
  else /*channel == BLUE */
    {
      offset=0; m1=1; m2=2;
    }
  
  image=map;
  
  
  for(h=0;h<height;h++)
    for(w=0;w<width;w++,image+=3)
      {
	if( ( *(image)  >= lb &&  *(image)  <= hb) &&
	    (*(image+1) >= lg && *(image+1) <= hg) &&
	    (*(image+2) >= lr && *(image+2) <= hr))
	  {
	    
	    /* maybe add a normalizer here so the outputs are 
	       between 100-255ish for more varied usage? */
	    
	    *(image+offset) = 255;
	    *(image+m1) = 0;
	    *(image+m2) = 0;
	  }
	else
	  {
	    *(image)   = 0;
	    *(image+1) = 0;
	    *(image+2) = 0;
	  }
      }
  return PyInt_FromLong(0L);
}
	  
	
/*******************************
 *
 *Blob Structure Function Calls
 *
 ******************************/

Blob *makeBlob(Blob *b)
{
  /*b=(Blob *)malloc(sizeof(Blob));*/

  b->mass = 0;
  b->ul.x = 384;
  b->ul.y = 240;
  b->lr.x = 0;
  b->lr.y = 0;
  b->cm.x = 0;
  b->cm.y = 0;
  b->next = 0;
  
  return(b);
}

Blob *initBlob( Blob *b, int y, int x )
{

  b->mass = 1;
  
  b->ul.x=x;
  b->ul.y=y;
  b->lr.x=x;
  b->lr.y=y;

  b->cm.x=x;
  b->cm.y=y;
  
  b->next = 0;
}

Blob *addPixel( Blob *b, int y,int x )
{

  if( x < b->ul.x )
    b->ul.x = x;
  
  if( x > b->lr.x )
    b->lr.x = x;
  
  if( y < b->ul.y )
    b->ul.y = y;
  
  if( y > b->lr.y )
    b->lr.y = y;
  
  /* not correct */
  /*b->cm.x =( (float)(b->mass * b->cm.x + x) / (float)(b->mass+1) );
    b->cm.y =( (float)(b->mass * b->cm.y + y) / (float)(b->mass+1) );*/
  b->mass++;
  
  return (b);
}

Blob *joinBlob( Blob *self, Blob *other )
{
  
  if( other->ul.x < self->ul.x )
    self->ul.x = other->ul.x;

  if( other->lr.x > self->lr.x )
      self->lr.x = other->lr.x ;
  
  if( other->ul.y < self->ul.y )
    self->ul.y = other->ul.y;

  if( other->lr.y > self->lr.y )
    self->lr.y = other->lr.y;
 
  /* Not Correct */
  /*
    self->cm.x=( (self->mass * self->cm.x + other->mass * other->cm.x )/
    (self->mass + other->mass));
    self->cm.y=( (self->mass * self->cm.y + other->mass * other->cm.y)/
    (self->mass + other->mass));
  */
  
  self->mass += other->mass;

}

void deleteBlob( Blob *b )
{

  b->cm.x = 192;
  b->cm.y = 120;
  b->ul.x = 384;
  b->ul.y = 240;
  b->lr.x = 0;
  b->lr.x = 0;
  b->mass = 0;

}

int getBlobWidth( Blob *b )
{
  return( b->lr.x - b->ul.x );
}

int getBlobHeight( Blob *b )
{
  return( b->lr.y - b->ul.y );
}

int getBlobArea( Blob *b )
{
  return( getBlobWidth( b ) * getBlobHeight( b ) );
}

float getBlobDensity( Blob *b )
{
  return( (float)b->mass / (float)getBlobArea( b ) );
}

static PyObject *blobify(PyObject *self, PyObject *args)
{
  /** 
      This code is a way to find the largest blob.  It will 
      combine blobs if there is more than one.  However, given
      the colors that we are using in the project, it is 
      unlikely that we'll have more than one blob with the 
      same color (unless the same object is split into multiple 
      regions by some other object)
      
      The function works by looking at the top and left pixel
      to see if there is already a blob there.  It joins or adds
      the pixel to the blob, and merges blobs if they are connected.
  **/
  
  Blob bloblist[MAXBLOBS];
  
  int channel, width, height, low, high,sortmethod, drawBox;
  int w,h,n,m,i,j, k, l;
  int offset, mark1, mark2;
  int count;
  int minBlobNum=0, maxBlobNum=0;
  int maxBlobIndex=0;
  
  unsigned int blobdata[240][384]={0};
  
  int min_x,min_y,max_x,max_y,cm_x,cm_y,mass;
  
  unsigned char *image;
  PyObject *tuple;
  
  if(!PyArg_ParseTuple(args, "iiiiiii", &channel, &low, 
		       &high, &sortmethod,&drawBox, &width, &height))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to blobify");
      return NULL;
    }
  
  min_x = width;
  min_y = height;
  max_x = 0;
  min_x = 0;
  cm_x = 0;
  cm_y = 0;
  
  image = map;
  
  if(channel == BLUE)
    {
      offset = 0; mark1 = 1; mark2 = 2;
    }
  else if(channel == GREEN)
    {
      offset = 1; mark1 = 0; mark2 = 2;
    }
  else if(channel == RED)
    {
      offset = 2; mark1 = 0; mark2 = 1;
    }
  else
    perror("Invalid Channel\n");
  
  
  for(n=0;n<MAXBLOBS;n++)
    makeBlob(&bloblist[n]);
  
  count = 1;
  
  /*build the blobmap and construct unjoined Blob objects*/
  for(h=0;h<height;h++)
    {
      for(w=0;w<width;w++,image+=3)
	{
	  if(*(image+offset) >= low && *(image+offset) <= high )
	    {  
	      if(h == 0 && w == 0)
		{ /*in upper left corner - new blob */
		  
		    initBlob(&bloblist[count],h,w);
		    blobdata[h][w]= count;
		    count++;
		}
	      else if(w == 0)/*if in first col */
		{
		 
		  if( blobdata[h-1][w] != 0 )
		    {
		      addPixel(&bloblist[blobdata[h-1][w]],h,w);
		      blobdata[h][w]=blobdata[h-1][w];
		    }
		  else /*above is off -- new blob*/
		    {
		      initBlob(&bloblist[count], h,w);		      
		      blobdata[h][w]=count;
		      count++;
		    }
		}
	      else if(h == 0) /* in first row */
		{
		  if( blobdata[h][w-1] != 0 )
		    {
		      addPixel(&bloblist[blobdata[h][w-1]],h,w);
		      blobdata[h][w]= blobdata[h][w-1];
		    }
		  else  /* left is off -- new blob */
		    {
		      initBlob(&bloblist[count], h,w);
		      blobdata[h][w]=count;
		      count++;
		    }		    
		}
	      
	      else if( blobdata[h][w-1] != 0 && blobdata[h-1][w] != 0 )
		{
		  
		  /*
		    see if the pixel to left and on the top are the same blob and add 
		    this new pixel to the blob if they are 
		  */
		  if(blobdata[h][w-1] == blobdata[h-1][w])
		    {
		      addPixel(&bloblist[blobdata[h][w-1]],h,w);
		      blobdata[h][w] = blobdata[h][w-1];
		    }
		  else 
		    {
		      addPixel(&bloblist[blobdata[h][w-1]],h,w);		      
		      joinBlob(&bloblist[blobdata[h][w-1]],&bloblist[blobdata[h-1][w]]);
		      blobdata[h][w] = blobdata[h][w-1];

		      n = blobdata[h-1][w];		      
		      for(i=0;i<=h;i++)
			for(j=0;j<width;j++)
			  if(blobdata[i][j] == n)
			    blobdata[i][j] = blobdata[h][w-1];
		    }
		}
	      else
		{
		  if( blobdata[h][w-1] != 0 )
		    {
		      addPixel(&bloblist[blobdata[h][w-1]],h,w);		  
		      blobdata[h][w]=blobdata[h][w-1];		      
		    }
		  /*top is on -- old blob */
		  else if( blobdata[h-1][w] != 0 )
		    {		      
		      addPixel(&bloblist[blobdata[h-1][w]],h,w);
		      blobdata[h][w]=blobdata[h-1][w];
		    }
		  else /* neither left or top on. -- new blob.*/
		    {
		      initBlob(&bloblist[count],h,w);		      
		      blobdata[h][w]=count;		      
		      count++;
		    }
		}
	    }
	}
    }
  
  
  maxBlobIndex=1;
  switch(sortmethod)
    {
    case 0: /* Max Mass */
      for(n=1;n<MAXBLOBS;n++)
	if(bloblist[n].mass != 0)
	  if(bloblist[n].mass > bloblist[maxBlobIndex].mass)
	    maxBlobIndex=n;
      break;
    case 1: /* max area*/
      for(n=1;n<MAXBLOBS;n++)
	if(bloblist[n].mass != 0)
	  if(getBlobArea(&bloblist[n]) > getBlobArea(&bloblist[maxBlobIndex]))
	    maxBlobIndex=n;
      break;
  
    case 2: /* Max Density */
      for(n=1;n<MAXBLOBS;n++)
	if(bloblist[n].mass != 0)
	  if(getBlobDensity(&bloblist[n]) > getBlobDensity(&bloblist[maxBlobIndex]))
	    maxBlobIndex=n;
      break;
  }
  
  image=map;
  if(drawBox)
    {
      for(i=0; i<height; i++ )
	for(j=0; j<width; j++,image+=3 )
	  {
	    if(blobdata[i][j] == maxBlobIndex)
	      {
		*(image+offset) = high;
		*(image+mark1) = 0;
		*(image+mark2) = 0;
		
	      }
	    
	    if(((j >= bloblist[maxBlobIndex].ul.x && j <= bloblist[maxBlobIndex].lr.x) &&
		(i == bloblist[maxBlobIndex].ul.y || i == bloblist[maxBlobIndex].lr.y)) ||
	       ((j == bloblist[maxBlobIndex].ul.x || j == bloblist[maxBlobIndex].lr.x) &&
		(i >= bloblist[maxBlobIndex].ul.y && i <= bloblist[maxBlobIndex].lr.y)))
	      {
		*(image+offset) = 255;
		*(image+mark1) = 255;
		*(image+mark2) = 255;
	      }
	  }
    }
  
  
  min_x = bloblist[maxBlobIndex].ul.x;
  min_y = bloblist[maxBlobIndex].ul.y;
  max_x = bloblist[maxBlobIndex].lr.x;
  max_y = bloblist[maxBlobIndex].lr.y;
  /*cm_x  = bloblist[maxBlobIndex].cm.x;
    cm_y  = bloblist[maxBlobIndex].cm.y;*/
  mass  = bloblist[maxBlobIndex].mass;
  
  /* got max blob coordinates, return them. */
  
  tuple = Py_BuildValue("iiiii", min_x, min_y, max_x, max_y,mass); 
  
  return tuple; 
}  


static PyObject *mean_blur(PyObject *self, PyObject *args)
{
  int width,height,kernel;
  int w,h,i,j,x,temp;
  unsigned int average[3]={0};
  unsigned char *image;
  unsigned char *ptr;
  
  if(!PyArg_ParseTuple(args, "iii", &kernel, &width, &height))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to mean_blur");
      return NULL;
    }

  if(kernel <= 0)
    kernel = 1;
  else if(kernel % 2 == 0) 
    kernel--;
  
  x=(int)kernel/2;
  
  image = map+(x*width+x)*3;
  
  for(h=x;h<height-x;h++)
    {
      for(w=x;w<width-x;w++,image+=3)
	{
	  
	  ptr=image-(x*width+x)*3;
	  
	  /* calculate average color of surrounding pixels*/
	  for(i=0;i<kernel;i++)
	    {
	      for(j=0;j<kernel;j++,ptr+=3)
		{
		  average[BLUE] += *(ptr);
		  average[GREEN]+= *(ptr+1);
		  average[RED]  += *(ptr+2);
		}
	      /* bring ptr to next row */
	      ptr=ptr-(kernel*3);
	      ptr=ptr+width*3; /* bring ptr to next row */
      
	    }
	  
	  *(image) = average[BLUE] / (kernel*kernel);
	  *(image+1) = average[GREEN] / (kernel*kernel);
	  *(image+2) = average[RED] / (kernel*kernel);
	
	  average[BLUE] = 0;
	  average[GREEN] = 0;
	  average[RED] = 0;
	}
   }
  return PyInt_FromLong(0L);
}

static PyObject *color_histogram(PyObject *self, PyObject *args){
  /***** same as train_color, but accept tl,br coords and *****
   ***** do all calculations relative to that box         *****/
}


static PyObject *train_color(PyObject *self, PyObject *args){
  int i,j;
  int width,height;
  int depth=3,w=0,h=0;
  
  unsigned short int peak[3]={0};
  unsigned int average[3]={0};
  unsigned int bucket[3][8]={0};

  unsigned char *image;

  PyObject *tuple;  

  if(!PyArg_ParseTuple(args, "ii",&width, &height)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to trainColor");
    return NULL;
  }

  image = map;
  
  w=width/2 - 25;
  h=height/2 - 25;
 

  /*make histogram of object inside a 50x50 pixel box. in the center of the screen*/
  /********************************************* 
   * Put read in colors into respective buckets*
   * 0:0 -31    1:32-63    2:64-95    3:96-127 * 
   * 4:128-159  5:160-191  6:192-223  7:224-255*
   *********************************************/
  for(i=h;i<h+50;i++)
    for(j=w;j<w+50;j++)
      {

	image = map+(i*width+j)*depth;/* move image pointer to next pixel*/
	
	if(*(image)< 32)
	  bucket[BLUE][0]++;
	else if(*(image) < 64)
	  bucket[BLUE][1]++;
	else if(*(image) < 96)
	  bucket[BLUE][2]++;
	else if(*(image) < 128)
	  bucket[BLUE][3]++;
	else if(*(image) < 160)
	  bucket[BLUE][4]++;
	else if(*(image) < 192)
	  bucket[BLUE][5]++;
	else if(*(image) < 225)
	  bucket[BLUE][6]++;
	else
	  bucket[BLUE][7]++;
	
	if(*(image+1)< 32)
	  bucket[GREEN][0]++;
	else if(*(image+1) < 64)
	  bucket[GREEN][1]++;
	else if(*(image+1) < 96)
	  bucket[GREEN][2]++;
	else if(*(image+1) < 128)
	  bucket[GREEN][3]++;
	else if(*(image+1) < 160)
	  bucket[GREEN][4]++;
	else if(*(image+1) < 192)
	  bucket[GREEN][5]++;
	else if(*(image+1) < 225)
	  bucket[GREEN][6]++;
	else
	  bucket[GREEN][7]++;
	
	if(*(image+2)< 32)
	  bucket[RED][0]++;
	else if(*(image+2) < 64)
	  bucket[RED][1]++;
	else if(*(image+2) < 96)
	  bucket[RED][2]++;
	else if(*(image+2) < 128)
	  bucket[RED][3]++;
	else if(*(image+2) < 160)
	  bucket[RED][4]++;
	else if(*(image+2) < 192)
	  bucket[RED][5]++;
	else if(*(image+2) < 225)
	  bucket[RED][6]++;
	else
	  bucket[RED][7]++;
      }
  
  /* find bucket with most items in it.  the peak */
  for(i=0;i<8;i++)
    {
      if(bucket[RED][i] > bucket[RED][peak[RED]])
	peak[RED] = i;
      
      if(bucket[GREEN][i] > bucket[GREEN][peak[GREEN]])
	peak[GREEN] = i;

      if(bucket[BLUE][i] > bucket[BLUE][peak[BLUE]])
	peak[BLUE] = i;
    }
  
  /* figure out avg color of the peaks */
  for(i=h;i<h+50;i++)
    for(j=w;j<w+50;j++)
      {
	image = map+(i*width+j)*depth;
	
	switch(peak[BLUE])
	  {
	  case 0:
	    if(*(image) < 32)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  case 1:
	    if(*(image) >= 32 && *(image) < 64)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  case 2:
	    if(*(image) >= 64 && *(image) < 96)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  case 3:
	    if(*(image) >= 96 && *(image) < 128)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  case 4:
	    if(*(image) >= 128 && *(image) < 160)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  case 5:
	    if(*(image) >= 160 && *(image) < 192)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  case 6:
	    if(*(image) >= 192 && *(image) < 224)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
  	  case 7:
	    if(*(image) >= 224)
	      average[BLUE]= average[BLUE] + *(image);
	    break;
	  default:
	    printf("ERROR IN BLUE\n");
	  }
	
	switch(peak[GREEN])
	  {
	  case 0:
	    if(*(image+1) < 32)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  case 1:
	    if(*(image+1) >= 32 && *(image+1) < 64)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  case 2:
	    if(*(image+1) >= 64 && *(image+1) < 96)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  case 3:
	    if(*(image+1) >= 96 && *(image+1) < 128)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  case 4:
	    if(*(image+1) >= 128 && *(image+1) < 160)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  case 5:
	    if(*(image+1) >= 160 && *(image+1) < 192)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  case 6:
	    if(*(image+1) >= 192 && *(image+1) < 224)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
  	  case 7:
	    if(*(image+1) >= 224)
	      average[GREEN]= average[GREEN] + *(image+1);
	    break;
	  default:
	    printf("ERROR IN GREEN\n");
	  }

	switch(peak[RED])
	  {
	  case 0:
	    if(*(image+2) < 32)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  case 1:
	    if(*(image+2) >= 32 && *(image+2) < 64)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  case 2:
	    if(*(image+2) >= 64 && *(image+2) < 96)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  case 3:
	    if(*(image+2) >= 96 && *(image+2) < 128)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  case 4:
	    if(*(image+2) >= 128 && *(image+2) < 160)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  case 5:
	    if(*(image+2) >= 160 && *(image+2) < 192)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  case 6:
	    if(*(image+2) >= 192 && *(image+2) < 224)
	      average[RED] = average[RED] + *(image+2);
	    break;
  	  case 7:
	    if(*(image+2) >= 224)
	      average[RED] = average[RED] + *(image+2);
	    break;
	  default:
	    printf("ERROR IN RED\n");
	  }
      }

  average[RED] =(int)(average[RED]/bucket[RED][peak[RED]]);
  average[GREEN] =(int)(average[GREEN]/bucket[GREEN][peak[GREEN]]);
  average[BLUE] = (int)(average[BLUE]/bucket[BLUE][peak[BLUE]]);
  
  
  tuple = Py_BuildValue("iii", 
			average[RED],
			average[GREEN],
			average[BLUE]);


  /* return the avg colors */
  return( tuple );
}


static PyObject *gaussian_blur(PyObject *self, PyObject *args)
{
  int width,height,offset,m1,m2;
  int x,y,temp;
  int depth = 3;

  unsigned char *image;
  unsigned char *out;
  
  if(!PyArg_ParseTuple(args, "ii", &width, &height))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to gaussian_blur");
      return NULL;
    }
  image = map;
  

  out = (unsigned char*)malloc(sizeof(char)*height*width*depth);

  
  /******************************
    here it says image[(x-1)+(y+1)*width] 
    if it is changed to image[(x-depth+offset)+(y+depth)*width]
    it should work for rgb (or bgr as the case may be)
    -----------------------------------------------------
     this means we will probably need another for loop for
     offset, as we probably want to blur for all channels
     ---------------------------------------------------
       Get each of the surrounding pixels weighted value
       top, left, right, and bottom weighing 2x
       diagonals weighing 1x
       pixel itself weighing 4x
       and take the average
       --------------------------------------------
       I think *out is just the output buffer, which
       in this case we want to be *image, so I think all
       those parts can be omitted
  ******************************************/

  for (y=1;y<height-1;y++)
    for (x=1;x<width-1;x++)
      for(offset=0;offset<depth;offset++)
      {
	temp=image[(x-depth+offset+y*width)*depth+offset];
	temp+=2*image[(x-depth+y*width)*depth+offset];
	temp+=image[(x-depth+(y+1)*width)*depth+offset];
	temp+=2*image[(x+(y-1)*width)*depth+offset];
	temp+=4*image[(x+y*width)*depth+offset];
	temp+=2*image[(x+(y+1)*width)*depth+offset];
	temp+=image[(x+depth+offset+(y-1)*width)*depth+offset];
	temp+=2*image[(x+depth+offset+y*width)*depth+offset];
	temp+=image[(x+depth+offset+(y+1)*width)*depth+offset];
	temp/=16;
	out[(x+offset+y*width)*depth+offset] = temp;
      }

  image = map;
  for (y=1;y<height-1;y++)
    for (x=1;x<width-1;x++)
      for(offset=0;offset<depth;offset++)
      	image[(x+y*width)*depth+offset] = out[(x+y*width)*depth+offset] ;
  
  return PyInt_FromLong(0L);

} 


static PyObject *save_image(PyObject *self, PyObject *args)
{
  int w, h;
  int i, j;
  char *filename; 
  unsigned char *p;
  FILE *fptr;
  
  if(!PyArg_ParseTuple(args, "iis", &w, &h, &filename))
    {
      PyErr_SetString(PyExc_TypeError, 
		      "Invalid arguments to saveImageInBuffer");
      return NULL;
    }
  /*  printf("file name: %s\n", filename);*/
  
  p=map;  
  
  if ((fptr=fopen(filename, "w+"))==NULL)
    {
      PyErr_SetString(PyExc_TypeError, 
		      "Unable to open file");
      return NULL;
    }
  else
    {
      fprintf(fptr, "P3\n%d %d\n 255\n", w, h);
      
      for (i=0; i<h; i++) {
	for (j=0; j<w; j++) {
	  fprintf(fptr, "%d %d %d\n", *(p+2), *(p+1), *p); 
	  p += 3;  
	}
      }
      fprintf(fptr,"\n");
      fclose(fptr);
    }
  return PyInt_FromLong(0L);
}



/*************************  END HISTOGRAM.C ********************/





static PyMethodDef grabImageMethods[] = {
  {"grab_image", grab_image, METH_VARARGS, "Grab an image from the camera"},
  {"free_image", free_image, METH_VARARGS, "Free memory from a grabbed image"},
  {"refresh_image", refresh_image, METH_VARARGS, "Refresh the image"},

  {"super_red", super_red, METH_VARARGS, "Compute super red in place"},
  {"super_blue", super_blue, METH_VARARGS, "Compute super blue in place"},
  {"super_green", super_green, METH_VARARGS, "Compute super green in place"},
  {"super_yellow", super_yellow, METH_VARARGS, "Compute super yellow in place"},
  {"super_white", super_white, METH_VARARGS, "Compute super white in place"},
  {"super_color", super_color, METH_VARARGS, "Compute super color in place"},
  {"color_filter", color_filter, METH_VARARGS, "Compute color filter in place"},
  {"blobify", blobify, METH_VARARGS, "Compute max blob in place"},
  {"train_color", train_color, METH_VARARGS, "Get the best fitting color"},
  {"mean_blur", mean_blur, METH_VARARGS, "Perform Mean blur in place"},
  {"gaussian_blur",gaussian_blur,METH_VARARGS,"Perform gaussianBlur in place"},
  {"train_color", train_color, METH_VARARGS, "Trains on a specific color"},
  {"save_image", save_image, METH_VARARGS, "Saves the buffer to a ppm image"},
  {NULL, NULL, 0, NULL}
};




void initgrabImage(void){
  (void) Py_InitModule("grabImage", grabImageMethods);
}
