
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

v4lcap.o: v4lcap.c v4lcap.h
	$(CC) $(CPPFLAGS) -c v4lcap.c -o v4lcap.o

_v4l.so: v4l.o V4L.o v4lcap.o
	$(CC) $(CPPFLAGS) -shared v4lcap.o v4l.o V4L.o ../vision/Vision.o $(LIBDIRS) -o $@ $(LIBS)

V4L.o:: V4L.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

V4L.cc: V4L.i V4L.h
	swig -python -c++ -o $@ $<

v4l.o: V4L.cc
	$(CC) -c $(PYTHON_INCLUDE) $^ -o $@

clean::
	$(RM) *~ 

cleanall::
	$(RM) *.so *.o
