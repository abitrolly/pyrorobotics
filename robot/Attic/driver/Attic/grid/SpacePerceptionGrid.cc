#include<limits.h>
#include<math.h>
#include"SpacePerceptionGrid.h"
#include<geometry/geometry.h>
#include<stdio.h>

#include<assert.h>

# define min(x, y) ((x<=y)?x:y)
# define max(x, y) ((x>=y)?x:y)

SpacePerceptionGrid::SpacePerceptionGrid(int w, int h, int low, 
					 int high, float overshoot){
  data = new float[w*h];
  grid = new float*[h];
  for(int i=0; i<h; i++)
    grid[i] = data + i*w;
  width  = w;
  height = h;
  lowerBound=low;
  upperBound = high;
  this->overshoot = overshoot;
  reset();
}

SpacePerceptionGrid::~SpacePerceptionGrid(){
  delete[] data;
  delete[] grid;
}

void SpacePerceptionGrid::reset(){
  for(int i=0; i<width; i++)
    for(int j = 0; j<height; j++)
      data[j*width + i] = 0;
}

void SpacePerceptionGrid::recenter(int dx, int dy){
  int top    = max(0, min(height / 2 + dy, height / 2));
  int bottom = max(0, min(height / 2 - dy, height / 2));
  int left   = max(0, min(width / 2 + dx, width / 2));
  int right  = max(0, min(width / 2 - dx, width / 2));

  /* create and init temporary array */
  float tmp[height][width];
  for(int i = 0; i < height; i++) 
    for(int j = 0; j < width; j++) {
      tmp[i][j] = 0;
    }

  /* copy a part of data */
  for(int i = height / 2 - top; i < height / 2 + bottom; i++) 
    for(int j = width / 2 - left; j < width / 2 + right; j++) {  
      assert((i >= 0 && i < height) && (j >= 0 && j < width));
      tmp[i][j] = grid[i][j]; 
      }  

  /* clear the grid */
  for(int i = 0; i < height; i++)
    for(int j = 0; j < width; j++) {
      assert((i >= 0 && i < height) && (j >= 0 && j < width));
      grid[i][j] = 0;
    }

  /* overwrite data */
  for(int i = height / 2 - top; i < height / 2 + bottom; i++)
    for(int j = width / 2 - left; j < width / 2 + right; j++) {
      assert((i + dy >= 0) && (i + dy < height) && 
	     (j + dx >= 0) && (j + dx < width));
      grid[i + dy][j + dx] = tmp[i][j];
    } 
}

float** SpacePerceptionGrid::getref() {
  return grid;
}

void SpacePerceptionGrid::copyregion(float **a, 
				     float **b,
				     int x,
				     int y,
				     int w, 
				     int h){
  printf("x: %d, y: %d, w: %d, h: %d\n", x, y, w, h);
  for(int i = y; i < y + h; i++) {
    for(int j = x; j < x + w; j++) {
      /* assert(i >= 0); 
      assert(i < h);
      assert(j >= 0); 
      assert(j < w); */
      assert(i - y >= 0);
      assert(i - y < h);
      assert(j - x >= 0);
      assert(j - x < w);
      // printf("i: %d, j: %d, ", i, j);
      //b[i][j] += a[i - y][j - x]; // too much redundancy
      //b[i][j] = (a[i - y][j - x] + b[i][j]) / 2 ;
      if (a[i - y][j - x] > 0 ) b[i][j] += 10;
      else if (a[i - y][j - x] < 0 ) b[i][j] += -5;
      
      if(b[i][j] > upperBound)
	b[i][j] = upperBound - 1; // 1 should be delta
      if(b[i][j] < lowerBound)
	b[i][j] = lowerBound + 1; // 1 should be delta
    }
    //printf("\n");
  }
}

float SpacePerceptionGrid::get(int x,int y){
  if((x < 0) || (x >= width))
    return -10000;
  if((y < 0) || (y >= height))
    return -10000;
  return grid[x][y];
}

void SpacePerceptionGrid::update(float xsrc, 
				 float ysrc, 
				 float xdst, 
				 float ydst, 
				 float angle,
				 float delta,
				 int hit){

  float p1[2];
  float p2[2];
  float p0[2];
  float p3[2];
  float p4[2];

  p0[0] = xsrc;
  p0[1] = ysrc;

  /* Need to rotate with respect to src, not origin  */

  float xdiff = xdst - xsrc;
  float ydiff = ydst - ysrc;

  p1[0] = xdiff*cos(angle/2.0) - ydiff*sin(angle/2.0);
  p1[1] = xdiff*sin(angle/2.0) + ydiff*cos(angle/2.0);  

  p2[0] = xdiff*cos(-angle/2.0) - ydiff*sin(-angle/2.0);
  p2[1] = xdiff*sin(-angle/2.0) + ydiff*cos(-angle/2.0);
  
  p3[0] = p1[0]*overshoot;
  p3[1] = p1[1]*overshoot;

  p4[0] = p2[0]*overshoot;
  p4[1] = p2[1]*overshoot;

  p1[0] += xsrc; p1[1] += ysrc;
  p2[0] += xsrc; p2[1] += ysrc;
  p3[0] += xsrc; p3[1] += ysrc;
  p4[0] += xsrc; p4[1] += ysrc;

  if(hit){
    updateGridTriangle(p0,p3,p4,-delta);
    updateGridTriangle(p0,p1,p2,2*delta);
  }
  else updateGridTriangle(p0,p1,p2,delta);
}

void SpacePerceptionGrid::decay(float delta){
  for(int i=0; i<width*height; i++)
    data[i] += delta;
}

void SpacePerceptionGrid::updateGridPoint(int x,int y, float delta){
  if((x < 0) || (x >= width))
    return;
  if((y < 0) || (y >= height))
    return;
  
  grid[x][y] += delta;
  if(grid[x][y] > upperBound)
    grid[x][y] -= delta;
  if(grid[x][y] < lowerBound)
    grid[x][y] -= delta;

}

void SpacePerceptionGrid::updateGridRow(int y, 
					int xmin, int xmax, 
					float delta){
  int x;

  if(xmin > xmax){
    x = xmin;
    xmin = xmax;
    xmax = x;
  }
  for(x=xmin; x<=xmax; x++) 
    updateGridPoint(x,y,delta);
}

void SpacePerceptionGrid::updateGridLine(float* p0,
					 float* p1,
					 float delta){
  // This will update grid on a line
  int y; float x;
  float *from,*to,dx;
  
  if(p0[1] > p1[1]){
    from = p1;
    to = p0;
  }
  else {
    from = p0;
    to = p1;
  }

  dx = to[1] - from[1];

  if(dx == 0){
    updateGridRow((int)p0[1],(int)p0[0],(int)p1[1],delta); //this needs floor/ceil stuff.
    return;
  }

  dx = (to[0] - from[0]) / dx;
  
  x=from[0];
  for(y=(int)ceil(from[1]);y<=to[1];y++,x+=dx){
    updateGridRow((int)y,(int)x,(int)(x+dx),delta);
  }
}

void SpacePerceptionGrid::updateGridTriangle(float* p0,
					     float* p1,
					     float* p2,
					     float delta){
  float* pts[3];
  float miny = INT_MAX; //(surely this is big enough?)
  float maxy = INT_MIN;
  float x[2];
  int y,ic,i;
  float isect[2] ;
  float la[2] = {INT_MAX,0},lb[2] = {INT_MIN,0};
  float t;

  pts[0] = p0; pts[1] = p1; pts[2] = p2;
  
  // DSB: I changed the ceil's to floor's based on experiments
  // SBM: Liberal bastard...
  
  for(i=0; i<3; i++){
    if(pts[i][1] < miny)
      miny = floor(pts[i][1]);
    if(pts[i][1] > maxy)
      maxy = ceil(pts[i][1]);
    if(pts[i][0] < la[0])
      la[0] = ceil(pts[i][0]);
    if(pts[i][0] > lb[0])
      lb[0] = floor(pts[i][0]);
  }
 
 for(y=(int)miny; y<=maxy; y++){
    la[1] = lb[1] = y;
    x[0] = x[1] = INT_MAX;
    for(i=0,ic=0; (i<3) && (ic<2); i++) {
      if(intersectLineSeg(la,lb,pts[i],pts[(i+1)%3],isect))
        x[ic++] = isect[0];
    }
    if (x[0] != INT_MAX) {
      if(x[0] > x[1]){
	t = x[0]; x[0] = x[1]; x[1] = t;
      }
      updateGridRow((int)y,(int)x[0],(int)x[1],delta);
    }
  }
}



