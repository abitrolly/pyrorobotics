SO = .so
OBJS = grabImage.o grabImage$(SO)

include ../../Makefile.cfg
include ../../Makefile.src

v4lcap.o: v4lcap.c v4lcap.h
	$(CC) $(CFLAGS) -c v4lcap.c -o v4lcap.o

grabImage.o: grabImage.c v4lcap.h
	$(CC) $(PYTHON_INCLUDE) $(CCSHARED)  $(CFLAGS) -c grabImage.c

grabImage$(SO):  grabImage.o v4lcap.o
	$(LD)  -shared grabImage.o v4lcap.o -o grabImage$(SO)

cleanall::
	$(RM) *.tga
