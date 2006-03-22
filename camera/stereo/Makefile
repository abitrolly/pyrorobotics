OBJS = _stereo.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../device/
CPPFLAGS = -O3 -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBS= -lstdc++ -ldl -lpthread

../device/Device.o: ../device/Device.h ../device/Device.cpp
	cd ../device/; make

_stereo.so: stereo.o Stereo.o 
	$(CC) $(CPPFLAGS) -shared stereo.o Stereo.o ../device/Device.o -o $@ $(LIBS)

Stereo.o:: Stereo.cpp Stereo.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c Stereo.cpp

Stereo.cc: Stereo.i Stereo.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o Stereo.cc Stereo.i

stereo.o: Stereo.cc 
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) Stereo.cc -o $@

clean::
	$(RM) *~ *.so *.o stereo.py Stereo.cc

