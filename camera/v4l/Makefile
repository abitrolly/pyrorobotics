SO = .so
OBJS = grabImage.o v4lcap.o

include ../../Makefile.cfg

grabImage$(SO): $(OBJS)
	$(LD)  -shared $(OBJS) -o grabImage$(SO)

v4lcap.o: v4lcap.c v4lcap.h
	$(CC) $(CFLAGS) -c v4lcap.c -o v4lcap.o

grabImage.o: grabImage.c v4lcap.h ../vision/vision.c ../vision/vision.h \
		../vision/visionMethods.h
	$(CC) $(PYTHON_INCLUDE) $(CCSHARED) $(CFLAGS) -c grabImage.c

clean::
	$(RM) *.tga grabImage$(SO) *.o *~
