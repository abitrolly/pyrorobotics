CC = gcc
OBJ = intersect.o vector.o volume.o geometry.o 
BIN  = test
LIB = libgeometry.so
MODULE = geometrymodule.so

PYTHONINCLUDE = -I/usr/local/include/python2.1

CFLAGS = -Wall -g
LDFLAGS = -L. -lgeometry -lm


%module.c : %.i %.h
	swig -python -o $@  $<

%module.o : %module.c
	gcc -c $(PYTHONINCLUDE) -o $@ $<

%module.so : %module.o
	gcc -nodefaultlibs -nostdlib -shared $(LDFLAGS) -o $@ $<

lib%.so : %.o
	gcc -nodefaultlibs -nostdlib -shared -o $@ $^


all : $(OBJ) $(LIB) $(BIN) $(MODULE)

libgeometry.so : $(OBJ)

clean :
	rm -f $(OBJ) $(LIB) $(MODULE) $(BIN) *~
