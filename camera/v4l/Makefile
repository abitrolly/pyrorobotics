
OBJS = _v4l.so

include ../../Makefile.cfg
include ../../Makefile.src

CPPFLAGS = -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE)

LIBDIRS= -L/usr/X11R6/lib
LIBS= -lstdc++ -lX11 -lXt -lXm -ldl -lpthread  -lXp -lXext

_v4l.so: v4l.o V4L.o
	$(CC) $(CPPFLAGS) -shared v4l.o V4L.o ../vision/Vision.o $(LIBDIRS) -o $@ $(LIBS)

V4L.o:: V4L.cpp ../vision/Vision.o
	$(CC) $(CPPFLAGS) -o $@ -c V4L.cpp

V4L.cc: V4L.i V4L.h ../vision/Vision.o
	swig -python -c++ -o $@ V4L.i

v4l.o: V4L.cc ../vision/Vision.o
	$(CC) -c $(PYTHON_INCLUDE) V4L.cc -o $@

clean::
	$(RM) *~ 

cleanall::
	$(RM) *.so *.o
