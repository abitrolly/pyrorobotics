OBJS = SpacePerceptionGrid.o
BIN  = 
LIB = 
MODULE = spgmodule.so
SRC = SpacePerceptionGrid.cc SpacePerceptionGrid.h
CLEAN = $(OBJS) $(LIB) $(MODULE) $(BIN) *~

CFLAGS = -Wall -g -I../../../
LDFLAGS = -L$(PYRO)/geometry -lm -lgeometry -L../../../lib

everything : $(OBJS) $(LIB) $(BIN) $(MODULE)

include ../../../Makefile.src

%module.cc : %.i 
	swig -c++ -python -o $@  $<

%module.o : %module.cc $(SRC)
	gcc -c $(PYTHON_INCLUDE) -o $@ $<

%module.so : %module.o
	gcc -shared $(LDFLAGS) $(OBJS) -o $@ $<

%.o : %.cc
	gcc -c $(CFLAGS) $< -o $@

