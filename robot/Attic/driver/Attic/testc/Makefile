OBJS = testcmodule.o testc.o
CLEAN = testc.o testcmodule.c testcmodule.o testcmodule.so

include ../../../Makefile.cfg
include ../../../Makefile.src

testcmodule.so : testcmodule.o testc.o
	ld -shared testcmodule.o testc.o -o testcmodule.so

testcmodule.o : testcmodule.c
	gcc -c $(PYTHON_INCLUDE) testcmodule.c -o testcmodule.o

testcmodule.c : testc.i testc.h
	swig -python -o testcmodule.c testc.i

testc.o : testc.c testc.h
	gcc -c testc.c -o testc.o


