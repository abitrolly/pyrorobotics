
#include<assert.h>
#include<malloc.h>

#include"volume.h"
#include"util.h"

typedef 
struct triangle{
  float* vtx[3];
  struct triangle* adj[3];
  float* edg[3][2];
  int inuse;
  int inside;
} triangle;


typedef
struct triangleArray{
  triangle* tris;
  int szTris;
  int lowest;
} triangleArray;


triangleArray* newTriangleArray(){
  triangleArray* ta;
  ta = malloc(sizeof(triangleArray));
  ta->tris = NULL;
  ta->szTris = 0;
  ta->lowest = 0;
  return ta;
}

void delTriangleArray(triangleArray* ta){
  assert(ta);
  if(ta->tris)
    free(ta->tris);
  free(ta);
}


triangle* getTriangle(triangleArray* tap){
  int i;

  while(1){ //try until we succeed (twice at most)
    for(i=tap->lowest; i<tap->szTris; i++){
      if(!tap->tris[i].inuse){
	tap->tris[i].inuse = 1;
	tap->lowest = i+1; //we've checked all before..
	return tap->tris+i;
      }
    }
    //none free, resize array
    tap->tris = realloc(tap->tris,(tap->szTris+100)*sizeof(triangle));
    assert(tap->tris);
    tap->lowest = tap->szTris;
    tap->szTris += 100;
  }
}

void freeTriangle(triangleArray* tap,triangle* tp){
  int index = tp - tap->tris;
  assert(index < tap->szTris);
  assert(index > 0);
  
  tap->tris[index].inuse = 0;
  if(tap->lowest > index)
    tap->lowest = index;
}



void printTriangle(triangle* t){
  iprintln("%p:{-(%2.2f,%2.2f,%2.2f)-%p-(%2.2f,%2.2f,%2.2f)-%p-(%2.2f,%2.2f,%2.2f)-%p}",
	   t,
	   t->vtx[0][0],t->vtx[0][1],t->vtx[0][2],t->adj[0],
	   t->vtx[1][0],t->vtx[1][1],t->vtx[1][2],t->adj[1],
	   t->vtx[2][0],t->vtx[2][1],t->vtx[2][2],t->adj[2]
	   );
}


/**
 * given four points make a tetrahedron
 * that has correct winding
 */
void addTetrahedron(triangleArray* tap,
		     float* v0,
		     float* v1,
		     float* v2,
		     float* v3){
  triangle* T[4];
  int i;

  for(i=0; i<4; i++)
    T[i] = getTriangle(tap);

  T[0]->vtx[0] = v0;
  T[0]->adj[0] = T[2];
  T[0]->vtx[1] = v1;
  T[0]->adj[1] = T[3];
  T[0]->vtx[2] = v2;
  T[0]->adj[2] = T[1];

  T[1]->vtx[0] = v1;
  T[1]->adj[0] = T[0];
  T[1]->vtx[1] = v0;
  T[1]->adj[1] = T[3];
  T[1]->vtx[2] = v3;
  T[1]->adj[2] = T[2];

  T[2]->vtx[0] = v2;
  T[2]->adj[0] = T[0];
  T[2]->vtx[1] = v1;
  T[2]->adj[1] = T[1];
  T[2]->vtx[2] = v3;
  T[2]->adj[2] = T[3];

  T[3]->vtx[0] = v2;
  T[3]->adj[0] = T[0];
  T[3]->vtx[1] = v0;
  T[3]->adj[1] = T[1];
  T[3]->vtx[2] = v3;
  T[3]->adj[2] = T[2];
}


int pointInFrontOfTriangle(float* point, triangle* tri){
  if(volumeTetrahedron(point,
		       tri->vtx[0],
		       tri->vtx[1],
		       tri->vtx[2]) 
     > 0)
    return 1;
  return 0;
}



typedef
struct edgeList{
  int* edge;
  triangle** tri;
  int size;
  int index;
}edgeList;

edgeList* newEdgeList(){
  edgeList* list = malloc(sizeof(edgeList));
  assert(list);
  list->edge = NULL;
  list->tri = NULL;
  list->tri = 0;
  list->index = 0;
  return list;
}

void delEdgeList(edgeList* el){
  if(el->edge)
    free(el->edge);
  if(el->tri)
    free(el->tri);
  free(el);
}

int getEdgeListIndex(edgeList* el){
  if(el->index == el->size){
    el->edge = realloc(el->edge,sizeof(int)*(el->size+10));
    el->tri = realloc(el->tri,sizeof(triangle*)*(el->size+10));
    assert(el->edge && el->tri);
    el->size += 10;
  }
  return el->index++;
}

int cvxhull3d_incrementFindEdge(triangle* t,
			      float* point,
			      triangleArray* tap,
			      edgeList** el){
  int i,idx;


  if(!pointInFrontOfTriangle(point,t))
    return 0;

  if(t->inside)
    return 1;
  t->inside = 1; //make sure we don't get called again
  
  if(!el)
    *el = newEdgeList();


  for(i=0; i<3; i++)
    if(!cvxhull3d_incrementUpdate(t->adj[i],point,tap,el)){
      idx = getEdgeListIndex(*el);
      (*el)->edge[idx] = i;
      (*el)->tri[idx] = t;
    }

  return 1;
}

/** 
 * cvxhull3d_increment
 *
 * find a triangle that point to add is in front of.
 *  if none than return, point is inside the hull
 *  else update the hull.
 */
void cvxhull3d_increment(triangleArray* tap, float* point){
  int t,i;
  edgeList* el;
  triangle** newtri;

  //check to see if the point is inside or outside the hull
  for(t=0; t<tap->szTris; t++)
    if( tap->tris[t].inuse 
	&& cvxhull3d_incrementFindEdge(tap->tris+t,point,tap,&el)){

      //add new triangles
      newtri = malloc(sizeof(triangle*)*el->size);
      for(t=0; t<el->size; t++)
	newtri[t] = getTriangle(tap);

      //???

      //remove old triangles
      for(t=0; t<el->size; t++)
	if(el->tri[t].inuse)
	  freeTriangle(tap,el->tri[t]);

      delEdgeList(el);
      return;
    }

}


/**
 * cvxhull3d_incremental
 *
 * In:
 *   float* nP
 *     number of points in input set
 *   float** P 
 *     an array of points 
 * Out:
 *  triangle* T
 *     an array of triangles
 *  int t
 *     how many triangles
 */
triangleArray* cvxhull3d_incremental(int nP,float** P,int* tp){
  //  triangle* T = (triangle*) malloc(sizeof(triangle)*2*nP+4);//maximum
  triangleArray* tap = newTriangleArray();
  int p;

  assert(nP > 4);

  addTetrahedron(tap,
		  P[0],P[1],
		  P[2],P[3]);

  for(p=4; p<nP; p++)
    cvxhull3d_increment(tap,P[p]);

  return tap;
}


void cvxhull3d_test(){
  float pts[12][3] = {
    {0,0,0},
    {1,0,0},{0,1,0},{0,0,1}, //faces
    {1,1,1},{-1,-1,-1},
    {-1,1,1},{1,-1,1},{1,1,-1},
    {1,-1,-1},{-1,1,-1},{-1,-1,1}
  };
  
  /*
  float* ppts[] = {pts[0],pts[1],pts[2],
		   pts[3],pts[4],pts[5],
		   pts[6],pts[7],pts[8],
		   pts[9],pts[10],pts[11]};
  */
  triangleArray* T = newTriangleArray();
  int i;

  iprintln("makeTetrahedron()");
  addTetrahedron(T,
		  pts[0],pts[1],
		  pts[2],pts[3]);

  iprintln(" Faces:");
  iup();
  for(i=0; i<4; i++){
    printTriangle(T->tris+i); //assuming its the first 4
    freeTriangle(T,T->tris+i);
  }
  delTriangleArray(T);
  idn();

  T = newTriangleArray();
}


