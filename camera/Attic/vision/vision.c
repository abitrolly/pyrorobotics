
static PyObject *super_red(PyObject *self, PyObject *args)
{
  int w, h, channel,m1,m2, lighten;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "iiii", &channel, &lighten, &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_red");
    return NULL;
  }

  m1=(channel+1)%3;
  m2=(channel+2)%3;
  
  p=(unsigned char *)map;
  
  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = *(p+2) - (*(p+1) + *p);
      
      if (temp<0)
	*(p+channel) = 0;
      
      else{
	if(lighten)
	  {
	    if(temp+60 > 255)
	      temp = 195;
	    *(p+channel) = temp+60;
	  }
	else
	  *(p+channel) = temp;
      }
      *(p+m1) = 0;
      *(p+m2) = 0;
      p += 3;
    }
  }
  
  return PyInt_FromLong(0L);
}  

static PyObject *super_blue(PyObject *self, PyObject *args)
{
  int w, h, channel, m1, m2, lighten;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "iiii", &channel, &lighten, &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_blue");
    return NULL;
  }

  m1=(channel+1)%3;
  m2=(channel+2)%3;
  
  p = (unsigned char *)map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = *p - (*(p+1) + *(p+2));
      if (temp<0)
	*(p+channel) = 0;
      
      else
	{
	  if(lighten)
	    {
	      if(temp+60 > 255)
		temp = 195;
	      *(p+channel) = temp+60;
	    }
	  else
	    *(p+channel) = temp;
	}
      
      *(p+m1) = 0;
      *(p+m2) = 0;
      p += 3;
    }
  }
  
  return PyInt_FromLong(0L);
}  

static PyObject *super_green(PyObject *self, PyObject *args)
{
  int channel, w, h, m1,m2, lighten;
  int i, j, temp;
  unsigned char *p;
  
  if(!PyArg_ParseTuple(args, "iiii", &channel, &lighten, &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_green");
    return NULL;
  }
  
  m1=(channel+1)%3;
  m2=(channel+2)%3;
  
  p=(unsigned char *)map;
  
  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = *(p+1) - (*p + *(p+2));
      if (temp<0)
	*(p+channel) = 0;

      else
	{
	  if(lighten)
	    {
	      if(temp+60 > 255)
		temp = 195;
	      *(p+channel) = temp+60;
	    }
	  else
	    *(p+channel) = temp;
	}
      
      *(p+m1) = 0;
      *(p+m2) = 0;
      p += 3;
    }
  }

  return PyInt_FromLong(0L);
}  

static PyObject *super_magenta(PyObject *self, PyObject *args)
{
  int w, h, channel, m1, m2, lighten;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "iiii", &channel, &lighten, &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_yello");
    return NULL;
  }

  m1=(channel+1)%3;
  m2=(channel+2)%3;

  p=(unsigned char *)map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = (*p + *(p+2))/2 - *(p+1);
      /*temp = *(p+2) - *(p+1);*/
      
      if (temp<0)
	*(p+channel) = 0;
      
      else
	{
	  if(lighten)
	    {
	      if(temp+60 > 255)
		temp = 195;
	      *(p+channel) = temp+60;
	    }
	  else
	    *(p+channel) = temp;
	}
      
      *(p+m1) = 0;
      *(p+m2) = 0;
      p += 3;
    }
  }
  
  return PyInt_FromLong(0L);
}  


static PyObject *super_yellow(PyObject *self, PyObject *args)
{
  int w, h, channel, m1, m2, lighten;
  int i, j, temp;
  unsigned char *p;
  
  if(!PyArg_ParseTuple(args, "iiii", &channel, &lighten, &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_yellow");
    return NULL;
  }
  
  m1=(channel+1)%3;
  m2=(channel+2)%3;
  
  p=(unsigned char *)map;
  
  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp =(int)((*(p+1)*2/3 + *(p+2)*1/3)/2 - *p);
      /*temp = *(p+1) - *p;*/
      
      if (temp<0)
	*(p+channel) = 0;

      else
	{
	  if(lighten)
	    {
	      if(temp+60 > 255)
		temp = 195;
	      *(p+channel) = temp+60;
	    }
	  else
	    *(p+channel) = temp;
	}

      *(p+m1) = 0;
      *(p+m2) = 0;
      p += 3;
    }
  }
  
  return PyInt_FromLong(0L);
}  


static PyObject *super_cyan(PyObject *self, PyObject *args)
{
  int w, h, channel, m1, m2, lighten;
  int i, j, temp;
  unsigned char *p;

  if(!PyArg_ParseTuple(args, "iiii", &channel, &lighten, &w, &h)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to super_yellow");
    return NULL;
  }

  m1=(channel+1)%3;
  m2=(channel+2)%3;

  p=(unsigned char *)map;

  for (i=0; i<h; i++) {
    for (j=0; j<w; j++) {
      temp = (*p + *(p+1))/2 - *(p+2);
      /*temp = *(p+2) - *p;*/

      if (temp<0)
	*(p+channel) = 0;

      else
	{
	  if(lighten)
	    {
	      if(temp+60 > 255)
		temp = 195;
	      *(p+channel) = temp+60;
	    }
	  else
	    *(p+channel) = temp;
	}

      *(p+m1) = 0;
      *(p+m2) = 0;
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
  
  image=(unsigned char *)map;
  
  
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
  if(self->mass != 0 && other->mass != 0)
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
      
      other->mass = 0;
    }
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

/* not correct, 1 pixel is very dense.  */
/*
  float getBlobDensity( Blob *b )
  {
  return( (float)b->mass / (float)getBlobArea( b ) );
  }
*/


void sortBlobs(int sortMethod, Blob bloblist[], int indexes[], int size)
{
  int i,j;
  int rankTable[MAXBLOBS];
  
  
  for(i=0; i<MAXBLOBS; i++)
    rankTable[i] = i;
  
  switch(sortMethod)
    {
      
    case 0:/* Mass */
      for(i=1; i < size+1; i++)
	for(j=i+1; j< MAXBLOBS; j++)
	  if(bloblist[rankTable[i]].mass < bloblist[rankTable[j]].mass)
	    SWAP(rankTable[i],rankTable[j]);
      break;
      
    case 1: /* Area */
      for(i=1; i < size+1; i++)
	for(j=i+1; j< MAXBLOBS; j++)
	  /* automattically swap out 0 mass from i spot*/
	  if(bloblist[rankTable[i]].mass == 0 ||
	     (bloblist[rankTable[j]].mass != 0 &&
	      getBlobArea(&bloblist[rankTable[i]]) <
	      getBlobArea(&bloblist[rankTable[j]])))
	    SWAP(rankTable[i],rankTable[j]); 
      break;
    
    }
  
  for(i=1;i<size+1;i++)
    indexes[i-1]= rankTable[i];
  
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
  
  int channel, width, height, low, high,sortmethod, size, drawBox;
  int w,h,n,m,i,j, k, l;
  int offset, mark1, mark2;
  int count;
  int minBlobNum=0, maxBlobNum=0;

  int maxIndex[5]={0};
  unsigned int blobdata[240][384]={0};
  
  unsigned char *image;
  PyObject *tuple;
  
  if(!PyArg_ParseTuple(args, "iiiiiiii", &channel, &low, 
		       &high, &sortmethod, &size, &drawBox, &width, &height))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to blobify");
      return NULL;
    }
  
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
		      
		      /*deleteBlob(&bloblist[blobdata[h-1][w]]);*/
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

  sortBlobs(sortmethod, bloblist, maxIndex,size);

  image=map;

  if(drawBox)
    {
      for(i=0; i<height; i++ )
	for(j=0; j<width; j++,image+=3 )
	  for(k=0;k<size;k++)
	    {
	      if(blobdata[i][j] == maxIndex[k])
	      {
		*(image+offset) = high;
		*(image+mark1) = 0;
		*(image+mark2) = 0;
		
	      }
	  
	      if(bloblist[maxIndex[k]].mass > 0 )
		if(((j >= bloblist[maxIndex[k]].ul.x && j <= bloblist[maxIndex[k]].lr.x) &&
		    (i == bloblist[maxIndex[k]].ul.y || i == bloblist[maxIndex[k]].lr.y)) ||
		   ((j == bloblist[maxIndex[k]].ul.x || j == bloblist[maxIndex[k]].lr.x) &&
		    (i >= bloblist[maxIndex[k]].ul.y && i <= bloblist[maxIndex[k]].lr.y)))
		  {
		    *(image+offset) = 255;
		    *(image+mark1) = 255;
		    *(image+mark2) = 255;
		  }
	    }
    }
  


  switch(size)
    {
    case 1:
      tuple = Py_BuildValue("iiiii",bloblist[maxIndex[0]].ul.x,
			    bloblist[maxIndex[0]].ul.y,bloblist[maxIndex[0]].lr.x,
			    bloblist[maxIndex[0]].ul.x,bloblist[maxIndex[0]].mass);
      break;
	   
    case 2:
      tuple = Py_BuildValue("iiiiiiiiii",bloblist[maxIndex[0]].ul.x,
			    bloblist[maxIndex[0]].ul.y,bloblist[maxIndex[0]].lr.x,
			    bloblist[maxIndex[0]].lr.y,bloblist[maxIndex[0]].mass,
			    bloblist[maxIndex[1]].ul.x,
			    bloblist[maxIndex[1]].ul.y,bloblist[maxIndex[1]].lr.x,
			    bloblist[maxIndex[1]].lr.y,bloblist[maxIndex[1]].mass);
      break;
    
    case 3:
      tuple = Py_BuildValue("iiiiiiiiiiiiiii",bloblist[maxIndex[0]].ul.x,
			    bloblist[maxIndex[0]].ul.y,bloblist[maxIndex[0]].lr.x,
			    bloblist[maxIndex[0]].lr.y,bloblist[maxIndex[0]].mass,
			    bloblist[maxIndex[1]].ul.x,bloblist[maxIndex[1]].ul.y,
			    bloblist[maxIndex[1]].lr.x,bloblist[maxIndex[1]].lr.y,
			    bloblist[maxIndex[1]].mass,
			    bloblist[maxIndex[2]].ul.x,bloblist[maxIndex[2]].ul.y,
			    bloblist[maxIndex[2]].lr.x,bloblist[maxIndex[2]].lr.y,
			    bloblist[maxIndex[2]].mass);
      break;

    case 4:
      tuple = Py_BuildValue("iiiiiiiiiiiiiiiiiiii",bloblist[maxIndex[0]].ul.x,
			    bloblist[maxIndex[0]].ul.y,bloblist[maxIndex[0]].lr.x,
			    bloblist[maxIndex[0]].lr.y,bloblist[maxIndex[0]].mass,
			    bloblist[maxIndex[1]].ul.x,bloblist[maxIndex[1]].ul.y,
			    bloblist[maxIndex[1]].lr.x,bloblist[maxIndex[1]].lr.y,
			    bloblist[maxIndex[1]].mass,
			    bloblist[maxIndex[2]].ul.x,bloblist[maxIndex[2]].ul.y,
			    bloblist[maxIndex[2]].lr.x,bloblist[maxIndex[2]].lr.y,
			    bloblist[maxIndex[2]].mass,
			    bloblist[maxIndex[3]].ul.x,bloblist[maxIndex[3]].ul.y,
			    bloblist[maxIndex[3]].lr.x,bloblist[maxIndex[3]].lr.y,
			    bloblist[maxIndex[3]].mass);

      break;

    case 5:
      tuple = Py_BuildValue("iiiiiiiiiiiiiiiiiiiiiiiii",bloblist[maxIndex[0]].ul.x,
			    bloblist[maxIndex[0]].ul.y,bloblist[maxIndex[0]].lr.x,
			    bloblist[maxIndex[0]].lr.y,bloblist[maxIndex[0]].mass,
			    bloblist[maxIndex[1]].ul.x,bloblist[maxIndex[1]].ul.y,
			    bloblist[maxIndex[1]].lr.x,bloblist[maxIndex[1]].lr.y,
			    bloblist[maxIndex[1]].mass,
			    bloblist[maxIndex[2]].ul.x,bloblist[maxIndex[2]].ul.y,
			    bloblist[maxIndex[2]].lr.x,bloblist[maxIndex[2]].lr.y,
			    bloblist[maxIndex[2]].mass,
			    bloblist[maxIndex[3]].ul.x,bloblist[maxIndex[3]].ul.y,
			    bloblist[maxIndex[3]].lr.x,bloblist[maxIndex[3]].lr.y,
			    bloblist[maxIndex[3]].mass,
			    bloblist[maxIndex[4]].ul.x,bloblist[maxIndex[4]].ul.y,
			    bloblist[maxIndex[4]].lr.x,bloblist[maxIndex[4]].lr.y,
			    bloblist[maxIndex[4]].mass);
      break;
    }
  /* got blob coordinates, return them. */  
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

void greyscale( unsigned int depth, unsigned int width, unsigned int height )
{
  unsigned char *image;
  unsigned int x, y, value;
 
  image = map;

  for (y=0; y<height; y++)
    for(x=0; x<width; x++)
    {
      value = (int)(image[(x+y*width)*depth]+image[(x+y*width)*depth+1]+image[(x+y*width)*depth+2])/3;

      image[(x+y*width)*depth]=   value;
      image[(x+y*width)*depth+1]= value;
      image[(x+y*width)*depth+2]= value;
    }

}


static PyObject *grey_scale(PyObject *self, PyObject *args) 
{
  unsigned int width;
  unsigned int height;
  unsigned int depth;

  if(!PyArg_ParseTuple(args, "iii", &depth, &width, &height) ) 
  {
    PyErr_SetString(PyExc_TypeError, 
		    "Invalid arguments to saveImageInBuffer");
    return;
  }
  
  greyscale( depth, width, height );
  
  return PyInt_FromLong(0L);

}


/* calculates sobel operator in x direction */
static PyObject *sobel(PyObject *self, PyObject *args) 
{
  unsigned int i, j, tempx, tempy, height, width, thresh, offset, depth=3;
  unsigned char *image;
  unsigned char *out;
  
  unsigned int a,b,d,f,g,z,c,e,h,gc, sobscale;

  if(!PyArg_ParseTuple(args, "iii", &thresh, &width, &height) ) 
  {
    PyErr_SetString(PyExc_TypeError, 
		    "Invalid arguments to saveImageInBuffer");
    return;
  }


  out = (unsigned char *)malloc(sizeof(char)*width*height*depth);
    
  image = map;
  
  for (j=0;j<height*width*depth;j++)
    out[j]=0;

  offset = 0;
  sobscale = 1;

  i = j = 0;
  
  for (j=0;j<height-2;j++)
  {
    a = image[(j*width+i)*depth];
    b = image[(j*width+(i+1))*depth];
    d = image[((j+1)*width+i)*depth];
    f = image[((j+2)*width+i)*depth];
    g = image[((j+2)*width+(i+1))*depth];
    z = image[(j*width+i)*depth];
    
    for (i=0;i<width-2;i++) 
    {
      c = image[(j*width+(i+2))*depth];
      e = image[((j+1)*width+(i+2))*depth];
      h = image[((j+2)*width+(i+2))*depth];

      tempx = (a+d+f) - (c+e+h);
      if( tempx < 0 ) tempx = -1*tempx;
      
      tempy = (a+b+c) - (f+g+h);
      if( tempy < 0 ) tempy = -1*tempy;

      gc = sobscale * sqrt(tempx*tempx+tempy*tempy);
      gc = offset+gc;
      gc = (gc>255)? 0 : 255 - gc;

      out[(j*width+i)*depth] = gc;
      out[(j*width+i)*depth+1] = gc;
      out[(j*width+i)*depth+2] = gc;

      a=b;
      b=c;
      d=z;
      f=g;
      g=h;
      z=e;

    }
    i=0;

  }

  image = map;
  for (j=0;j<height;j++)
    for (i=0;i<width;i++)
      for(offset=0;offset<depth;offset++)
	image[(i+j*width)*depth+offset] = out[(i+j*width)*depth+offset] ;

  free(out);
 
  return PyInt_FromLong(0L);
}

int getMiddleIndex(int median[4][400], int kernel)
{
  
  int i,j;
  int rankTable[400];
  
  
  for(i=0; i<kernel*kernel; i++)
    rankTable[i] = i;
  
  for(i=0; i < kernel*kernel; i++)
    for(j=i+1; j< kernel*kernel; j++)
      if(median[3][rankTable[i]] > median[3][rankTable[j]])
	SWAP(rankTable[i],rankTable[j]);
  
  return(rankTable[(int)((kernel*kernel)/2)]);
}

static PyObject *median_blur(PyObject *self, PyObject *args)
{
  int width,height,kernel,mid;
  int w,h,i,j,x, moveVal, offset, temp=0;
  int median[4][400]={-1};  /*enough for 20x20(huge) Kernel */
  int intensity = 3;
  int depth = 3;
  unsigned char *image, *out, *outptr;
  unsigned char *ptr;
  
  if(!PyArg_ParseTuple(args, "iii", &kernel, &width, &height))
    {
      PyErr_SetString(PyExc_TypeError, "Invalid arguments to mean_blur");
      return NULL;
    }

  out = (unsigned char *)malloc(sizeof(char)*width*height*depth);

  if(kernel <= 0)
    kernel = 1;
  else if(kernel % 2 == 0) 
    kernel--;
  
  x=(int)kernel/2;
  
  moveVal = x*width+x;

  image = map+(moveVal)*3;
  outptr = out+(moveVal)*3;
  
  for (j=0;j<height*width*depth;j++)
    out[j]=0;

  offset = 0;

  for(h=x;h<height-x;h++)
    {
      for(w=x;w<width-x;w++,image+=3,outptr+=3)
	{
	  ptr=image-(moveVal)*3;
	  temp=0;
	 
	  /* find middle color of surrouding pixels */
	  for(i=0;i<kernel;i++)
	    {
	      for(j=0;j<kernel;j++,ptr+=3,temp++)
		{
		  median[BLUE][temp]  = *(ptr);
		  median[GREEN][temp] = *(ptr+1);
		  median[RED][temp]  = *(ptr+2);
		  median[intensity][temp]=0.3*(*(ptr+2)) + 0.59*(*(ptr+1)) + 0.11*(*(ptr));
		}
	      /* bring ptr to next row */
	      ptr=ptr-(kernel*3);
	      ptr=ptr+width*3; /* bring ptr to next row */
	    }
	  
	  /* get median intensity index */
	  mid=getMiddleIndex(median, kernel);

	  *outptr = median[BLUE][mid];
	  *(outptr+1) = median[GREEN][mid];
	  *(outptr+2) = median[RED][mid];

	}
    }

  image = map;
  outptr = out;
  for (j=0;j<height;j++)
    for (i=0;i<width;i++)
      for(offset=0;offset<depth;offset++)
	image[(i+j*width)*depth+offset] = outptr[(i+j*width)*depth+offset] ;

  free(out);

  
  return PyInt_FromLong(0L);
}

