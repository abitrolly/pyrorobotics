
OBJS = _vision.so

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

_vision.so: vision.o Vision.o
	$(CC) $(CPPFLAGS) -shared $^ $(LIBDIRS) -o $@ $(LIBS)

Vision.o:: Vision.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

Vision.cc: Vision.i Vision.h Vision.cpp
	swig -python -c++ -o $@ Vision.i

vision.o: Vision.cc
	$(CC) -c $(PYTHON_INCLUDE) $^ -o $@

clean::
	$(RM) *~ 

cleanall::
	$(RM) *.so *.o
