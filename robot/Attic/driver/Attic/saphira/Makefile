# author: Douglas Blank

OBJS = _lowlevel.so

include ../../../Makefile.cfg
include ../../../Makefile.src

SAPHIRA_LIB = -L$(SAPHIRA)/handler/obj -L../../../lib 
SAPHIRA_INC = -I$(SAPHIRA)/handler/include 

CPPFLAGS = -Wall -Wno-unused -DNTSC -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
        -DPYRO_VERSION=$(PYRO_VERSION) -D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
        -D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
        $(SAPHIRA_INC) $(PYTHON_INCLUDE) -Iinclude -g

LIBDIRS= -L/usr/X11R6/lib 
LIBS= -lstdc++ -lX11 -lXt -lXm -ldl -lpthread -lptzsys -lsfx -lXp -lXext
#LIBS= -lstdc++ -lX11 -lXt -lXm -ldl -lpthread -lptzsys -lsfx

../../../lib/_lowlevel.so: _lowlevel.so
	cp _lowlevel.so ../../../lib

obj/%.o : %.cpp
	mkdir obj | true
	$(CC) $(CPPFLAGS) -o $@ -c $< 

main: main.cpp obj/Saphira.o
	$(CC) $(CPPFLAGS) $^ -o $@ $(LIBDIRS) $(SAPHIRA_LIB) $(LIBS)

_lowlevel.so: lowlevel.o obj/Saphira.o
	$(CC) $(CPPFLAGS) -shared $^ $(SAPHIRA_LIB) $(LIBDIRS) -o $@ $(LIBS)

lowlevel.cc: Saphira.i Saphira.h
	swig -python -c++ -o $@ $<

lowlevel.o: lowlevel.cc
	$(CC) -c $(PYTHON_INCLUDE) $^ -o $@

clean::
	$(RM) obj/*.o
