SO = .so
OBJS = grabImage.o grabImage$(SO)

include ../../Makefile.src

grabImage.o: grabImage.c
	$(CC) $(PYTHON_INCLUDE) $(CCSHARED)  $(CFLAGS) -c grabImage.c

grabImage$(SO):  grabImage.o
	$(LD)  -shared grabImage.o  -o grabImage$(SO)
