OBJS = _fake.so

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

_fake.so: fake.o Fake.o 
	$(CC) $(CPPFLAGS) -shared fake.o Fake.o ../vision/Vision.o $(LIBDIRS) -o $@ $(LIBS)

Fake.o:: Fake.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

Fake.cc: Fake.i Fake.h
	swig -python -c++ -o $@ $<

fake.o: Fake.cc
	$(CC) -c $(PYTHON_INCLUDE) $^ -o $@

clean::
	$(RM) *~ 

cleanall::
	$(RM) *.so *.o
