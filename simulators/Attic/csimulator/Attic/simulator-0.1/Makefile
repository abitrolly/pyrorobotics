OBJ = WorldObject.o Triangle.o TriangleList.o World.o simulator.o BasicPhysicsObject.o SimpleObject.o
BIN  =  test mkobjs showobj
LIB = libsimulator.so

include ../Makefile.include

DEFINES = -D__USE_GL -D_GNU_SOURCE
LDFLAGS :=  $(LDFLAGS) $(GLLDFLAGS) -lgeometry -lstdc++ -ldl -lg++

libsimulator.so : $(OBJ)

