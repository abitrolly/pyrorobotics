include ../../../Config.mk

OBJ = SpacePerceptionGrid.o
BIN  = 
LIB = 
MODULE = spgmodule.so
SRC = SpacePerceptionGrid.cc SpacePerceptionGrid.h

CFLAGS = -Wall -g -I$(PYRO) 
LDFLAGS = -L$(PYRO)/geometry -lm -lgeometry

all : $(OBJ) $(LIB) $(BIN) $(MODULE)

%module.cc : %.i 
	swig -c++ -python -o $@  $<

%module.o : %module.cc $(SRC)
	gcc -c $(PYTHONINCLUDE) -o $@ $<

%module.so : %module.o
	gcc -shared $(LDFLAGS) $(OBJ) -o $@ $<

%.o : %.cc
	gcc -c $(CFLAGS) $< -o $@

clean :
	rm -f $(OBJ) $(LIB) $(MODULE) $(BIN) *~
