OBJS = intersect.o vector.o volume.o geometry.o 
BIN  = test
LIB = ../lib/libgeometry.so
MODULE = ../lib/geometrymodule.so
CLEAN = $(OBJS) $(LIB) $(MODULE) $(BIN) *~

everything : $(OBJS) $(LIB) $(BIN) $(MODULE)

include ../Makefile.cfg
include ../Makefile.src

CFLAGS = -Wall -g
LDFLAGS = -L. -lgeometry -lm -L../lib/

%module.c : %.i %.h
	swig -python -o $@  $<

%module.o : %module.c
	gcc -c $(PYTHON_INCLUDE) -o $@ $<

../lib/%module.so : %module.o
	gcc -nodefaultlibs -nostdlib -shared $(LDFLAGS) -o $@ $<

../lib/lib%.so : %.o
	gcc -nodefaultlibs -nostdlib -shared -o $@ $^

#libgeometry.so : $(OBJS)

