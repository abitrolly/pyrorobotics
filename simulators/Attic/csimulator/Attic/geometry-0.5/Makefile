
OBJ = vops.o mops.o intersect.o  scanline.o  volume.o  cvxhull2d.o util.o  Xform.o integer.o compareTest.o volumeTest.o vopsTest.o utilTest.o mopsTest.o
BIN  = test
LIB = libgeometry.so

include ../Makefile.include

DEFINES= -D__USE_GL -D_GNU_SOURCE
LDFLAGS := ${LDFLAGS} ${GLLDFLAGS} ${C++LDFLAGS} 

libgeometry.so : $(OBJ)

test : libgeometry.so
