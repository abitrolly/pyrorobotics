#include "3DGraphics.h"

3DGraphics::3DGraphics():
{
  RotateMatrixRobot = Matrix();
  RotateMatrixWorld = Matrix();
  mouse_x = 0;
  mouse_y = 0;
  
  m_bDoubleBuffer = true;
  m_bSolidPolygons = false;
}

void 3DGraphics::mousePressEvent()
{
  static time_t lastMidClick = (time_t)NULL; 
  m_Button = pMouseEvent->button();
  if (m_Button == MidButton) {
    if (lastMidClick && (time(NULL) - lastMidClick) < 1) {
      // A middle double click will move robot
      mouse_x = pMouseEvent->pos().x();
      mouse_y = pMouseEvent->pos().y();
      lastMidClick = (time_t)NULL;
    } else {
      lastMidClick = time(NULL);
    }
  } 
  mousex = pMouseEvent->pos().x();
  mousey = pMouseEvent->pos().y();
}

void 3DGraphics::mouseMoveEvent()
{
  if (pfROBOTVIEW) {
    if (m_Button == LeftButton) {
      RotateMatrixRobot = 
	Matrix::RotateYDeg(mousex-pMouseEvent->pos().x()) 
	* RotateMatrixRobot;
      RotateMatrixRobot = 
	Matrix::RotateXDeg(mousey-pMouseEvent->pos().y()) 
	* RotateMatrixRobot;
    } else if (m_Button == RightButton) {
      double scale = 1.0+((mousey-pMouseEvent->pos().y()) / 50.0);
      RotateMatrixRobot = 
	Matrix::Scale(
		      scale,
		      scale,
		      scale
		      ) * RotateMatrixRobot;
      RotateMatrixRobot = 
	RotateMatrixRobot *
	Matrix::RotateZDeg(mousex-pMouseEvent->pos().x()) ;
    } else if (m_Button == MidButton) {
      RotateMatrixRobot = 
	Matrix::Translate(mousex-pMouseEvent->pos().x(),
			  mousey-pMouseEvent->pos().y(),0.0) 
	* RotateMatrixRobot;
    }
  } else {
    if (m_Button == LeftButton) {
      RotateMatrixWorld = 
	Matrix::RotateYDeg(mousex-pMouseEvent->pos().x()) 
	* RotateMatrixWorld;
      RotateMatrixWorld = 
	Matrix::RotateXDeg(mousey-pMouseEvent->pos().y()) 
	* RotateMatrixWorld;
    } else if (m_Button == RightButton) {
      double scale = 1.0+((mousey-pMouseEvent->pos().y()) / 50.0);
      RotateMatrixWorld = 
	Matrix::Scale(
		      scale,
		      scale,
		      scale
		      ) * RotateMatrixWorld;
      RotateMatrixWorld = 
	RotateMatrixWorld *
	Matrix::RotateZDeg(mousex-pMouseEvent->pos().x()) ;
    } else if (m_Button == MidButton) {
      RotateMatrixWorld = 
	Matrix::Translate(mousex-pMouseEvent->pos().x(),
			  mousey-pMouseEvent->pos().y(),0.0) 
	* RotateMatrixWorld;
    }
  }
  mousex = pMouseEvent->pos().x();
  mousey = pMouseEvent->pos().y();
  
  repaint(FALSE);
}


inline void 3DGraphics::AddPerspective(Vertex3D & vert )
{
  double perspective;
  const double closeness = -2.0;
  if (vert.z < closeness) {
    perspective = scale / vert.z;
  } else {
    perspective = 1.0;
  }
  
  vert = vert * perspective;
}

/*
  This function will setup our clipping Frustum, this function must
  be called everytime the window is resized
*/
void 3DGraphics::SetSize(int width,int height )
{
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

/*
  This will actually clip a face, works on lines too
  
  Works by alternating lists to work on the previous one built, when done
  the final list is actually stored in the result list passed into
  the function
*/
void 3DGraphics::ClipFace(
			  const Vertex3D * verticies,long count, 
			  Vertex3D * result, long & resultcount)
{
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

void 3DGraphics::paintEvent () 
{
  
  int pref_paintmethod = 0;
  int pfPAINTERS = 1;
  
  /* get a little information about the screen */
  QRect geom = geometry();
  int width = geom.size().width(),height = geom.size().height();
  int centerx = width/2,centery = height/2;
  
  // should be in an onresize function
  SetSize(width +2, height+2 );
  
  // clipping stuff
  Vertex3D VertsIn[3],VertsOut[180],point;
  long lVertCount;
  PolygonHolder * polygon = NULL;
  PolygonList.SetSize(0L,500L);
  
  // matrix stack information
  const int MaxStackSize = 15;
  static Matrix MatrixStack[MaxStackSize];
  int StackTop = 0;
  
  Matrix matrix;
  
  // build our primitives list
  PrimitiveList primitives;
  primitives.SetSize(0L,500L);
  
  // need a pointer to the robot
  extern Robot * __Robot;
  
  /* want to draw out a grid structure */
  primitives.Add(new ColorPrim(0.7,0.7,0.7));
  
  // FIX: this should be gleaned from the sim world 
  // (if simulated)... otherwise? dynamic?
  for (int i = -30;i<=18;i++) {
    primitives.Add(new LinePrim(i,-30,0,i,18,0));
    primitives.Add(new LinePrim(-30,i,0,18,i,0));
  }
  
  // get our list from the engine
  Engine->UpdateDrawList(primitives);
  
  int pref_view = 0;
  
  // update our transforms matrix
  // *** The order of the operations in this command are important ***
  matrix = 
    // get the robot away from the screen
    Matrix::Translate(0,0,-75.0) *  
    // do the screen rotate
    (pfROBOTVIEW ? RotateMatrixRobot : RotateMatrixWorld) * 
    // this will let the robot rotate the world
    (pref_view == pfROBOTVIEW ?
     Matrix::RotateZRad(-__Robot->getActualRadth()) :
     // This will point 0 angle of world, up
     Matrix::RotateZRad(-PI/2)* 
     // tip down a bit:
     Matrix::RotateYDeg(50)) *
    // scale it
    Matrix::Scale(30,30,30);	
  
  // if reposition the robot, need matrix computed first
  if (mouse_y != 0.0 || mouse_x != 0.0) {
    double clickx = (((double)width) / 2.0  - mouse_x);
    double clicky = (((double)height) / 2.0 - mouse_y);
    printf("mouse: (%f, %f) scale = %f\n", clickx, clicky, scale);
    Vertex3D location = matrix.Inverse() * Vertex3D(0,0,0);
    Vertex3D direction = (matrix.Inverse() * Vertex3D(0,0,1)) - location;
    Vertex3D line = 
      (direction + Vertex3D( clickx, clicky, 0)).Unit();
    
    double a = (line + location).dot(Vertex3D(0,0,1));
    printf("a = %f\n", a);
    double b = location.dot(Vertex3D(0,0,1));
    printf("b = %f\n", b);
    double c = 1 / (1 - (a / b));
    printf("c = %f\n", c);
    Vertex3D v = (line * c) + location;
    
    printf("Inverse X = %f\n", v.x);
    printf("Inverse Y = %f\n", v.y);
    
    mouse_x = 0;
    mouse_y = 0;
  }
  
  QPointArray poly( 180 );
  int polycnt = 0;
  double redsave,greensave,bluesave;
  
  // begin painting
  QPainter paint;
  
  QPixmap pm(geometry().size());
  if (m_bDoubleBuffer) {
    paint.begin (&pm,this);
  }
  else {
    paint.begin( this );
  }
  
  paint.fillRect(0,0,width,height,QBrush(QColor(255,255,255)));
  
  for (int i=0;i<primitives.GetTop();i++) {
    switch(primitives[i]->type) {
    case Primitive::Text:
      VertsIn[0] = matrix 
	* Matrix::Translate(-__Robot->getActualX(),
			    -__Robot->getActualY(),0)
	* Vertex3D(
		   primitives[i]->data[0],
		   primitives[i]->data[1],
		   0
		   );
      
      ClipFace(VertsIn,2,VertsOut,lVertCount);
      if (!lVertCount)
	break;
      AddPerspective(VertsOut[0]);
      
      paint.drawText(
		     centerx+(int)VertsOut[0].x, 
		     centery-(int)VertsOut[0].y,
		     primitives[i]->tdata
		     );
      break;
      /*
	Going to draw a line
      */		
    case Primitive::Line:
      /* get the endpoints and transform them */
      VertsIn[0] = matrix 
	* Matrix::Translate(-__Robot->getActualX(),
			    -__Robot->getActualY(),0)
	* Vertex3D(
		   primitives[i]->data[0],
		   primitives[i]->data[1],
		   primitives[i]->data[2]
		   );
      VertsIn[1] = matrix 
	* Matrix::Translate(-__Robot->getActualX(),
			    -__Robot->getActualY(),0)
	* Vertex3D(
		   primitives[i]->data[3],
		   primitives[i]->data[4],
		   primitives[i]->data[5]
		   );
      
      ClipFace(VertsIn,2,VertsOut,lVertCount);
      if (!lVertCount)
	break;
      
      AddPerspective(VertsOut[0]);
      AddPerspective(VertsOut[1]);
      
      paint.drawLine(
		     centerx+(int)VertsOut[0].x, 
		     centery-(int)VertsOut[0].y,
		     centerx+(int)VertsOut[1].x,
		     centery-(int)VertsOut[1].y
		     );
      break;
      /*
	Going to draw a circle
      */
    case Primitive::Circle:
      for (double d=0,ds=0.2;d<6.28;d+=ds) {
				/* going to draw a circle the dirty way */
	VertsIn[0] = matrix 
	  * Matrix::Translate(-__Robot->getActualX(),
			      -__Robot->getActualY(),0)
	  * Vertex3D(
		     primitives[i]->data[0]+
		     primitives[i]->data[3]*cos(d),
		     primitives[i]->data[1]+
		     primitives[i]->data[3]*sin(d),
		     primitives[i]->data[2]
		     );
	
	VertsIn[1] = matrix 
	  * Matrix::Translate(-__Robot->getActualX(),
			      -__Robot->getActualY(),0)
	  * Vertex3D(
		     primitives[i]->data[0]+
		     primitives[i]->data[3]*cos(d+ds),
		     primitives[i]->data[1]+
		     primitives[i]->data[3]*sin(d+ds),
		     primitives[i]->data[2]
		     );
	
	
	
	ClipFace(VertsIn,2,VertsOut,lVertCount);
	
	if (!lVertCount)
	  continue;
	
	AddPerspective(VertsOut[0]);
	AddPerspective(VertsOut[1]);
	
	paint.drawLine(
		       centerx+(int)VertsOut[0].x, 
		       centery-(int)VertsOut[0].y,
		       centerx+(int)VertsOut[1].x,
		       centery-(int)VertsOut[1].y
		       );
      }
      
      break;
    case Primitive::FilledCircle:
      polycnt = 0;
      if (polygon)
	delete polygon;
      polygon = new PolygonHolder;
      polygon->r = redsave;
      polygon->g = greensave;
      polygon->b = bluesave;
      if (pref_paintmethod != pfPAINTERS)
	polygon->z = 100000;
      else
	polygon->z = 0;
      for (double d=0,ds=0.2;d<6.28;d+=ds) {
	/* going to draw a circle the dirty way */
	point = matrix 
	  * Matrix::Translate(-__Robot->getActualX(),
			      -__Robot->getActualY(),0)
	  * Vertex3D(
		     primitives[i]->data[0]+
		     primitives[i]->data[3]*cos(d),
		     primitives[i]->data[1]+
		     primitives[i]->data[3]*sin(d),
		     primitives[i]->data[2]
		     );
	polygon->points.Add( point );
	if (pref_paintmethod == pfPAINTERS) {
	  polygon->z += point.z;
	} else {
	  polygon->z = ((point.z < polygon->z) ? point.z :
			polygon->z);
	}
      }
      if (!m_bSolidPolygons) {
	ClipFace(
		 polygon->points,
		 polygon->points.GetTop(),
		 VertsOut,lVertCount
		 );
	
	delete polygon;
	polygon = NULL;
	
	if (!lVertCount) 
	  break;
	
	for (int j=0;j<lVertCount;j++) {
	  AddPerspective(VertsOut[j]);
	  poly[j] = QPoint (
			    centerx+(int)VertsOut[j].x,
			    centery-(int)VertsOut[j].y
			    );
	}
	paint.drawPolygon(poly, FALSE, 0, lVertCount); 
      } else {
	if( pfPAINTERS == pref_paintmethod)
	  polygon->z /= polygon->points.GetTop();
	PolygonList.Add(polygon);
	polygon = NULL;
      }
      break;
    case Primitive::Point:
      point = matrix 
	* Matrix::Translate(-__Robot->getActualX(),
			    -__Robot->getActualY(),0)
	* Vertex3D (
		    primitives[i]->data[0],
		    primitives[i]->data[1],
		    primitives[i]->data[2]
		    ) ;
      polygon->points.Add( point );
      if (pref_paintmethod == pfPAINTERS) {
	polygon->z += point.z;
      } else {
	polygon->z = ((point.z < polygon->z) ? point.z :
		      polygon->z);
      }
      break;
      
    case Primitive::Color:
      paint.setPen( QColor ( 
			    primitives[i]->data[0]*255,
			    primitives[i]->data[1]*255,
			    primitives[i]->data[2]*255
			    ) );
      redsave = primitives[i]->data[0];
      greensave = primitives[i]->data[1];
      bluesave = primitives[i]->data[2];
      
      break;
      
    case Primitive::Style:
      paint.setPen(QPen ( 
			 QColor ( 
				 primitives[i]->data[0]*255,
				 primitives[i]->data[1]*255,
				 primitives[i]->data[2]*255 ),
			 (unsigned int) primitives[i]->data[3],
			 (PenStyle) primitives[i]->data[4] 
			 ) );
      redsave = primitives[i]->data[0];
      greensave = primitives[i]->data[1];
      bluesave = primitives[i]->data[2];
      break;
      
    case Primitive::RobotStart:
      if (StackTop < MaxStackSize)
	MatrixStack[StackTop] = matrix;
      StackTop++;
      matrix = matrix*Matrix::RotateZRad(
					 primitives[i]->data[3]
					 );
      matrix = matrix*Matrix::Translate(
					primitives[i]->data[0],
					primitives[i]->data[1],
					primitives[i]->data[2]
					);
      break;
    case Primitive::RobotEnd:
      if (StackTop > 0) 
	matrix = MatrixStack[--StackTop];
      break;
    case Primitive::PolygonStart:
      polycnt = 0;
      if (polygon)
	delete polygon;
      polygon = new PolygonHolder;
      polygon->r = redsave;
      polygon->g = greensave;
      polygon->b = bluesave;
      if (pref_paintmethod != pfPAINTERS)
	polygon->z = 100000;
      else
	polygon->z = 0;
      break;
      
    case Primitive::PolygonEnd:
      if (!m_bSolidPolygons) {
	ClipFace(
		 polygon->points,
		 polygon->points.GetTop(),
		 VertsOut,lVertCount
		 );
	
	delete polygon;
	polygon = NULL;
	
	if (!lVertCount) 
	  break;
	
	
	for (int j=0;j<lVertCount;j++) {
	  AddPerspective(VertsOut[j]);
	  poly[j] = QPoint (
			    centerx+(int)VertsOut[j].x,
			    centery-(int)VertsOut[j].y
			    );
	}
	paint.drawPolygon(poly, FALSE, 0, lVertCount); 
      } else {
	if( pfPAINTERS == pref_paintmethod)
	  polygon->z /= polygon->points.GetTop();
	PolygonList.Add(polygon);
	polygon = NULL;
      }
      break;
    default:
      break;
    }
    if ( primitives[i] )
      delete primitives[i];
  }
  
  /* now we draw any polygons that may have been added */
  if ( m_bSolidPolygons && PolygonList.GetTop() > 0) {
    SortPolygonList();
    paint.setPen(NoPen);
    for (int i=0;i<PolygonList.GetTop();i++) {
      ClipFace(PolygonList[i]->points,
	       PolygonList[i]->points.GetTop(),
	       VertsOut,lVertCount);
      
      paint.setBrush( QColor ( 
			      PolygonList[i]->r*255,
			      PolygonList[i]->g*255,
			      PolygonList[i]->b*255
			      ) );
      
      delete PolygonList[i];
      if (!lVertCount) {
	
	continue;
      }
      
      
      for (int j=0;j<lVertCount;j++) {
	AddPerspective(VertsOut[j]);
	poly[j] = QPoint (
			  centerx+(int)VertsOut[j].x,
			  centery-(int)VertsOut[j].y
			  );
      }
      paint.drawPolygon(poly, FALSE, 0, lVertCount); 
    }
  }
  paint.end();
  
  if (m_bDoubleBuffer)
    bitBlt(this,0,0,&pm);
  
}

void 3DGraphics::SortPolygonList(void)
{
  int i,j;
  PolygonHolder * swap;
  
  for (i=0;i<PolygonList.GetTop();i++) 
    for (j=0;j<PolygonList.GetTop()-1;j++) {
      if (PolygonList[j]->z > PolygonList[j+1] -> z) {
	swap = PolygonList[j];
	PolygonList[j] = PolygonList[j+1];
	PolygonList[j+1] = swap;
      }
    }
}

void 3DGraphics::SortPolygonList(Vertex3D polylist[180], 
				 int polycnt)
{
  int i,j;
  Vertex3D swap;
  
  for (i=0;i<polycnt;i++) 
    for (j=0;j<polycnt-1;j++) {
      if (polylist[j].z > polylist[j+1].z) {
	swap = polylist[j];
	polylist[j] = polylist[j+1];
	polylist[j+1] = swap;
      }
    }
}
