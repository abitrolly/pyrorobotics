// Canvas class, indepenent of graphics

#include <math.h>
#include "Canvas3D.h"

Canvas3D::Canvas3D(int w, int h, char buffer[], int r) {
  rowstride = r;
  width = w;
  height = h;
  red = 0;
  green = 0;
  blue = 0;
  line_width = 2;
  buf = buffer;
  scale = 1.0;
}

void Canvas3D::SetSize(int width,int height ) {
  double a,c,s;
  
  // get the current scale
  if (width/2 > height/2)
    scale = width/2;
  else
    scale = height/2;
  
  a = atan2(width/2,scale);
  
  c = cos(a);
  s = sin(a);
  m_Frustum[0] = Vertex3D(c,0,-s);
  m_Frustum[1] = Vertex3D(-c,0,-s);
  
  a = atan2(height/2, scale);
  
  c = cos(a);
  s = sin(a);
  m_Frustum[2] = Vertex3D(0,c,-s);
  m_Frustum[3] = Vertex3D(0,-c,-s);
}

RGB *Canvas3D::getPixel(int x, int y) {
  RGB *rgb = new RGB(buf[y * rowstride + x * 3 + 0],
		     buf[y * rowstride + x * 3 + 1],
		     buf[y * rowstride + x * 3 + 2]);
  return rgb;
}


void Canvas3D::setPixel(int x, int y) {
  buf[y * rowstride + x * 3 + 0] = red; // (r, g, b) 
  buf[y * rowstride + x * 3 + 1] = green; // (r, g, b) 
  buf[y * rowstride + x * 3 + 2] = blue; // (r, g, b) 
}

void Canvas3D::draw_point(int x1, int y1) {
  if (line_width > 1) {
    for (int x = x1 - line_width/2; x < x1 + line_width/2; x++) {
      for (int y = y1 - line_width/2; y < y1 + line_width/2; y++) {
	setPixel(x, y);
      }
    }
  } else { 
    setPixel(x1, y1);
  }
}

void Canvas3D::draw_line(int x0, int y0, int x1, int y1 ) {
  // Bresenham's Method
  int dy = y1 - y0;
  int dx = x1 - x0;
  int stepx, stepy;
  if (dy < 0) { dy = -dy;  stepy = -1; } else { stepy = 1; }
  if (dx < 0) { dx = -dx;  stepx = -1; } else { stepx = 1; }
  dy <<= 1;                                 // dy is now 2*dy
  dx <<= 1;                                 // dx is now 2*dx
  draw_point(x0, y0);
  if (dx > dy) {
    int fraction = dy - (dx >> 1);          // same as 2*dy - dx
    while (x0 != x1) {
      if (fraction >= 0) {
	y0 += stepy;
	fraction -= dx;                     // same as fraction -= 2*dx
      }
      x0 += stepx;
      fraction += dy;                       // same as fraction -= 2*dy
      draw_point(x0, y0);
    }
  } else {
    int fraction = dx - (dy >> 1);
    while (y0 != y1) {
      if (fraction >= 0) {
	x0 += stepx;
	fraction -= dy;
      }
      y0 += stepy;
      fraction += dx;
      draw_point(x0, y0);
    }
  }
}
/*
  buf[y1 * rowstride + x1 * 3 + 0] = red; // (r, g, b) 
  buf[y1 * rowstride + x1 * 3 + 1] = green; // (r, g, b) 
  buf[y1 * rowstride + x1 * 3 + 2] = blue; // (r, g, b) 
  buf[y2 * rowstride + x2 * 3 + 0] = red; // (r, g, b) 
  buf[y2 * rowstride + x2 * 3 + 1] = green; // (r, g, b) 
  buf[y2 * rowstride + x2 * 3 + 2] = blue; // (r, g, b) 
*/

void Canvas3D::AddPerspective(Vertex3D & vert ) {
  double perspective;
  const double closeness = -2.0;
  if (vert.z < closeness) {
    perspective = scale / vert.z;
  } else {
    perspective = 1.0;
  }
  vert = vert * perspective;
}

void Canvas3D::ClipFace(const Vertex3D * verticies,long count, 
			Vertex3D * result, long & resultcount) {
  static double distances[1000];
  static Vertex3D List[1000];
  int current,next,origcount=count;	
  double dist1,dist2;
  Vertex3D * VertexList,* ResultList;
  
  // after all of the swapping, this is where the final list will be
  VertexList = result;
  // a temperary list for calculations
  ResultList = List;
  
  // this could just as easy be an if in the calculate disances
  for (int i=0;i<count;i++)
    VertexList[i] = verticies[i];
  
  // loop through each clipping plane
  for (int i=0;i<4;i++) {		
    
    /* pre calculate the distances */
    for (int j=0;j<count;j++) 
      distances[j] = m_Frustum[i].dot(VertexList[j]);
    
    /* init before the next loop */
    resultcount = 0;
    next = count-1;
    for (int j=0;j<count;j++) {
      
      current = next;
      next = j;
      
      dist1 = distances[current];
      dist2 = distances[next];
      
      // if the vertex is visible then add it
      if (dist1 > 0)
	ResultList[resultcount++] = VertexList[current];
      
      // if the current vertex and the next vertex lie on
      // different sides of the frustum plane then find
      // out where they intersect the plane and add
      // that vertex
      if ( (origcount > 2) || (j < count-1) )
	if ( ((dist1 > 0 && dist2 < 0) || 
	      (dist1 < 0 && dist2 > 0)) ) 
	  {
	    ResultList[resultcount++] = 
	      (VertexList[next] - VertexList[current]) *
	      (dist1/(dist1-dist2)) +
	      (VertexList[current]);
	  }
    }
    /* swap the lists */
    Vertex3D * swap;
    
    swap = VertexList;
    VertexList = ResultList;
    ResultList = swap;
    
    /* reset the count */
    count = resultcount;
  }
}

/*
 * A Seed Fill Algorithm
 * by Paul Heckbert
 * from "Graphics Gems", Academic Press, 1990
 *
 * user provides pixelread() and pixelwrite() routines
 */

/*
 * fill.c : simple seed fill program
 * Calls pixelread() to read pixels, pixelwrite() to write pixels.
 *
 * Paul Heckbert        13 Sept 1982, 28 Jan 1987
 */


typedef struct {short y, xl, xr, dy;} Segment;
/*
 * Filled horizontal segment of scanline y for xl<=x<=xr.
 * Parent segment was on line y-dy.  dy=1 or -1
 */

#define MAX 10000               /* max depth of stack */

#define PUSH(Y, XL, XR, DY)     /* push new segment on stack */ \
    if (sp<stack+MAX && Y+(DY)>=0 && Y+(DY)<=height) \
    {sp->y = Y; sp->xl = XL; sp->xr = XR; sp->dy = DY; sp++;}

#define POP(Y, XL, XR, DY)      /* pop segment off stack */ \
    {sp--; Y = sp->y+(DY = sp->dy); XL = sp->xl; XR = sp->xr;}

/*
 * fill: set the pixel at (x,y) and all of its 4-connected neighbors
 * with the same pixel value to the new pixel value nv.
 * A 4-connected neighbor is a pixel above, below, left, or right of a pixel.
 */

void Canvas3D::fill(int x, int y) { /* seed point */
  int l, x1, x2, dy;
  RGB ov(0, 0, 0);   /* old pixel value */
  RGB nv(red, green, blue); // current colors
  Segment stack[MAX], *sp = stack;    /* stack of filled segments */
  
  ov.set(getPixel(x, y));               /* read pv at seed point */
  if (ov.same(nv) || x<0 || x>width || y<0 || y>height) return;
  PUSH(y, x, x, 1);                   /* needed in some cases */
  PUSH(y+1, x, x, -1);                /* seed segment (popped 1st) */
  
  while (sp>stack) {
    /* pop segment off stack and fill a neighboring scan line */
    POP(y, x1, x2, dy);
    /*
     * segment of scan line y-dy for x1<=x<=x2 was previously filled,
     * now explore adjacent pixels in scan line y
     */
    for (x=x1; x>=width && ov.same(getPixel(x, y)); x--)
      setPixel(x, y);
    if (x>=x1) goto skip;
    l = x+1;
    if (l<x1) PUSH(y, l, x1-1, -dy);                /* leak on left? */
    x = x1+1;
    do {
      for (; x<=width && ov.same(getPixel(x, y)); x++)
	setPixel(x, y);
      PUSH(y, l, x-1, dy);
      if (x>x2+1) PUSH(y, x2+1, x-1, -dy);        /* leak on right? */
    skip:       
      for (x++; x<=x2 && !ov.same(getPixel(x, y)); x++);
      l = x;
    } while (x<=x2);
  }
}
