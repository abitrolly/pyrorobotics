SAPHIRA_LIB = -L$(SAPHIRA)/handler/obj -lsfx 
SAPHIRA_INC = -I$(SAPHIRA)/handler/include 
PYTHON_INC  = -I/usr/local/include/python2.1/ -I/home/dblank/Python-2.1.1/Include/ -I/home/dblank/Python-2.1.1/

CPPFLAGS = -Wall -Wno-unused -DNTSC -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
        -DPYRO_VER=$(PYRO_VER) -D_REENTRANT -DPOSIX -D__x86__ -D__linux__ \
        -D__OSVERSION__=2 -frepo -D USINGTHREADS -DLINUX -D_GNU_SOURCE \
        $(MOBILITY_INC) $(SAPHIRA_INC) $(PYTHON_INC) -Iinclude -g

LIBDIRS= -L/usr/X11R6/lib 
LIBS= -lstdc++ -lX11 -lXt -lXm -ldl -lpthread

all: lowlevelmodule.so 

obj/%.o : %.cpp
	mkdir obj | true
	gcc $(CPPFLAGS) -o $@ -c $< 

main: main.cpp obj/Saphira.o
	gcc $(CPPFLAGS) $^ -o $@ $(LIBDIRS) $(SAPHIRA_LIB) $(LIBS)

lowlevelmodule.so: lowlevelmodule.o obj/Saphira.o
	gcc $(CPPFLAGS) -shared $^ $(SAPHIRA_LIB) $(LIBDIRS) -o $@ $(LIBS)

lowlevelmodule.cc: Saphira.i Saphira.h
	swig -python -c++ -o $@ $<

lowlevelmodule.o: lowlevelmodule.cc
	gcc -c $(PYTHON_INC) $^ -o $@

clean :
	rm -f obj/* | true



