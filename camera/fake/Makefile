# C Camera + Vision Code
# Pyro: Python Robotics

SO = .so
OBJS = grabImage.o

all:: grabImage$(SO)

include ../../Makefile.cfg

grabImage.o: grabImage.c ../vision/vision.c ../vision/vision.h \
		../vision/visionMethods.h
	$(CC) $(PYTHON_INCLUDE) $(CCSHARED) $(CFLAGS) -c grabImage.c

grabImage$(SO): $(OBJS)
	$(LD) -shared $(OBJS) -o grabImage$(SO)

clean::
	$(RM) *.tga *$(SO) *.o *~
