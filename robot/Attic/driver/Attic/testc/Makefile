PYTHONINCLUDE= -I/usr/local/include/python2.0 -I/usr/local/lib/python2.0/config


testcmodule.so : testcmodule.o testc.o
	ld -shared testcmodule.o testc.o -o testcmodule.so

testcmodule.o : testcmodule.c
	gcc -c $(PYTHONINCLUDE) testcmodule.c -o testcmodule.o

testcmodule.c : testc.i testc.h
	swig -python -o testcmodule.c testc.i

testc.o : testc.c testc.h
	gcc -c testc.c -o testc.o


clean:
	rm testc.o testcmodule.c testcmodule.o testcmodule.so