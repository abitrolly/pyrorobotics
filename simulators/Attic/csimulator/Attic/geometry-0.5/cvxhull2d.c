#include<assert.h>
#include<limits.h>
#include<stdio.h>

#include "util.h"
#include"vops.h"

#include"cvxhull2d.h"


int (*cvxhull2D_fptr)(int nPts,float* pts) = grahams;


//sort pts by cvxhull. returns number of points in the
//cvx hull. (first ret val pts in pts are the hull in couterclockwise order)
int cvxhull2D(int nPts,float* pts){
  return cvxhull2D_fptr(nPts,pts);
}

void cvxhullSetAlgo2D(int algo){
  switch(algo){
  case CVXHULL_GIFTWRAP:
    cvxhullSetFunc2D(giftWrap2D);
    break;
  case CVXHULL_QUICKHULL:
    cvxhullSetFunc2D(quickHull2D);
    break;
  case CVXHULL_GRAHAMS:
    cvxhullSetFunc2D(grahams);
    break;
  default:
    printf("Invalid algorithm specified in %s. No change performed. \n",__PRETTY_FUNCTION__);
  }
}

void cvxhullSetFunc2D(int (*ch)(int nPts, float* pts)){
  assert(ch);
  cvxhull2D_fptr = ch;
}

int giftWrap2D(int nPts,float* pts){
  int i; //generic iterator
  int front; //'front' of the hull that is being 'wrapped'
  int minanglePt;
  float minangle,tmp;
  float edge[2] = { 0,1 };
  float tmpv0[2];
  float tmpv1[2];

  assert(nPts >= 3); 
  assert(pts);

  //find 'left-est' point,  it is in the hull so put it first.
  for(i=1; i<nPts; i++)
    if(pts[i*2] < pts[0])
      swap(2,pts,pts+i*2);

  //find first edge of the hull
  minangle = vangle(2,edge,vsub(2,pts,pts+2,tmpv0)); //all angles are above zero
  minanglePt = 1;
  for(i=front+2; i<nPts; i++){
    tmp = vangle(2,edge,vsub(2,pts,pts+i*2,tmpv0));
    if(tmp < minangle){
      minangle = tmp;
      minanglePt = i;
    }
  }

  swap(2,pts+1,pts+2*minanglePt); //found first edge. Time for the rest.
  
  //for each point in the hull
  for(front=0; front<nPts; front++){
    //find the next point in the hull
    for(i=front+1; i<nPts; i++){
      //angle between the last edge and the possible next edge
      tmp = vangle(2,vsub(2,pts+2*(front-1),pts+2*front,tmpv0),
	          vsub(2,pts+2*front,pts+2*i,tmpv1)
		  );
      //do we have a winner?
      if(tmp < minangle){
	minangle = tmp;
	minanglePt = i;
      }
    }
    
    //if the angle between the last edge and the edge to the first point
    //is the minimum we are done.
    if(minangle > 
       vangle(2,vsub(2,pts+2*(front-1),pts+2*front,tmpv0),
	     vsub(2,pts+2*front,pts,tmpv1)
	     )) {
      break;
    }
    swap(2,pts+front+1,pts+i);
  }
  return front; //the last point on the front is the end of the hull
}


int quickHull2D(int szS,float* S){
  assert(szS > 3);
  assert(0);
  /*
  //find the least and greatest
  swap(S,findLeast(2,0,S));
  swap(S+2,findGreatest(2,0,S));
  
  return quickHull2D_recurse(szS-2,S,S+1,S+2);
  */
  return 0;
}
/*
int quickHull2D_recurse(int szS, float* a, float* b,float* S){
  int rD,lD,lS,rS;
  float* c;

  if(szS == 0) 
    return 0;

  swap(S,findFarthest(a,b,S));
 
  c = S; 
  S++; 
   szS--; //pointer diddleing to simplify next segment. (remove c from S,c isin the hull)
  rD = szS-1; //points to next free elemnt at the end of S
   lD = 0; //points to first free element at start of S
  for(i=lD; i<=rD; i++){
    if(isRightOf(S+i,a,c)) //if its right of ac put at begin of array
      swap(S+i,S+lD++);
    else if(isRightOf(S+i,b,c))
      swap(S+i,S+rD--);   //if its right of bc put at end of array
  }

  rD++; //point to first element in right set

  lS = quickHull2D_recurse(lD,a,c,S);
  rS = quickHull2D_recuse(szS-rD,b,c,S+rD);

  for(i=0; i<rS;i++)
    swap(S+lS,S+rD+i);

  return lS+rS+1;
}
*/
int grahams(int nPts,float* pts){
  assert(0);
  return 0;
}

