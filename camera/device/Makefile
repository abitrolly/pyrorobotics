
OBJS = Device.o

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

Vision.o:: Vision.cpp Vision.h
	$(CC) $(CPPFLAGS) -o $@ -c $<

clean::
	$(RM) *~ 

cleanall::
	$(RM) *.so *.o
