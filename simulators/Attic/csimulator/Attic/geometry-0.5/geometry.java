public class geometry {
  public final static native void cgTest();
  public final static double TOLERANCE = .0001;

  public final static native int cvxhull2D(int jarg0, float [] jarg1);
  public final static native void cvxhullSetAlgo2D(int jarg0);
  public final static native int giftWrap2D(int jarg0, float [] jarg1);
  public final static native int quickHull2D(int jarg0, float [] jarg1);
  public final static native int grahams(int jarg0, float [] jarg1);
  public final static int DIM = 3;

  public final static native int isectSegSeg(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3, float [] jarg4);
  public final static native int isectLineSeg(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3, float [] jarg4);
  public final static native int isectRayPlane(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3, float [] jarg4);
  public final static native int isectRayTri(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3, float [] jarg4, float [] jarg5, float [] jarg6);
  public final static native int isectSegPlane(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3);
  public final static native int isectSegTri(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3, float [] jarg4, float [] jarg5);
  public final static native void scanConvertTriangle(int [] jarg0, int [] jarg1, int [] jarg2);
  public final static native void swap(int jarg0, float [] jarg1, float [] jarg2);
  public final static native float angle(int jarg0, float [] jarg1, float [] jarg2);
  public final static native float dot(int jarg0, float [] jarg1, float [] jarg2);
  public final static native float [] sub(int jarg0, float [] jarg1, float [] jarg2, float [] jarg3);
  public final static native float [] cross3D(float [] jarg0, float [] jarg1, float [] jarg2);
  public final static native float [] normalize(int jarg0, float [] jarg1);
  public final static native int vtoleq(int jarg0, float [] jarg1, float [] jarg2);
  public final static native float [] vecalloc(int jarg0);
  public final static native float [] vfree(float [] jarg0);
  public final static native float [] findLeast(int jarg0, int jarg1, float [] jarg2);
  public final static native float [] findGreatest(int jarg0, int jarg1, float [] jarg2);
  public final static native float volumeTetrahedron(float [] jarg0, float [] jarg1, float [] jarg2, float [] jarg3);
}
