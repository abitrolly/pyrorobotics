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

_fake.so: fake.o Fake.o ../vision/Vision.o
	$(CC) $(CPPFLAGS) -shared fake.o Fake.o ../vision/Vision.o $(LIBDIRS) -o $@ $(LIBS)

Fake.o:: Fake.cpp Fake.h ../vision/Vision.o
	$(CC) $(CPPFLAGS) -o $@ -c Fake.cpp

Fake.cc: Fake.i Fake.h ../vision/Vision.o
	swig -python -c++ -o Fake.cc Fake.i

fake.o: Fake.cc ../vision/Vision.o
	$(CC) -c $(PYTHON_INCLUDE) Fake.cc -o $@

clean::
	$(RM) *~ 

cleanall::
	$(RM) *.so *.o
