
OBJS = _vision.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../../camera/device/
CPPFLAGS = -O3 -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBS= -lstdc++ -ldl -lpthread

_vision.so: vision.o Vision.o ../../camera/device/Device.o
	$(CC) $(CPPFLAGS) -shared $^ $(LIBDIRS) -o $@ $(LIBS)

Vision.o:: Vision.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

Vision.cc: Vision.i Vision.h Vision.cpp
	swig $(INCLUDE) -python -c++ -o $@ Vision.i

vision.o: Vision.cc
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) $^ -o $@

clean::
	$(RM) *~ *.so *.o *.cc *.so *.pyc vision.py

