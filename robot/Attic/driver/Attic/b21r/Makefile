VPATH = include:obj:src

include ../../../Makefile.cfg
include ../../../Makefile.src

INCLUDE = $(MOBILITY_INC) -Iinclude

# The makefile also needs the following enviroment variables:
# $MOBILITY_ROOT, $MOBILITY_TOOLS

LIBS  = -lpthread -ldl -lc -lm  -lpthread -lncurses
MOBILITY_LIB = -L$(MOBILITY_ROOT)/lib -L$(MOBILITY_TOOLS)/lib \
	-lmby -lidlmby -lomniDynamic2 -lomniORB2 -ltcpwrapGK -lomnithread 
MOBILITY_INC = -I$(MOBILITY_ROOT)/include -I$(MOBILITY_TOOLS)/include \
	-I/usr/local/mobility-b-1.1.7-rh6.0/include/

CPPFLAGS = -Wall -Wno-unused -DNTSC -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-DXRCL_VER=$(XRCL_VER) -D_REENTRANT -DPOSIX -D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -D USINGTHREADS -DLINUX -D_GNU_SOURCE\
	$(PYTHON_INCLUDE) $(MOBILITY_INC) -Iinclude -g

B21R_OBJS = obj/B21R.o obj/Sonar.o obj/b21r.o \
	obj/Laser.o obj/Tactile.o obj/Robot.o obj/Sensor.o obj/Vector.o

#*******************************************************
#*************** These are the main targets ************
#*******************************************************

all:: _lowlevel.so

_lowlevel.so: lowlevel.o $(B21R_OBJS) 
	$(CC) $(CPPFLAGS) -shared $^ $(SAPHIRA_LIB) $(LIBDIRS) -o $@ $(LIBS) -lomnithread -L /usr/local/mobility-b-1.1.7-rh6.0/tools/lib -L/usr/local/mobility-b-1.1.7-rh6.0/lib/ -lmby -lomniORB2 -ltcpwrapGK -lmbybase -lIIW -lNMEA -lidlmby -lmbybxxbase -lmbycfr -lmbyserial -lmbyuser -lrFlex3 -lreflex -lreflex2 -lomniDynamic2 -lomniLC

lowlevel.o: lowlevel.cc
	gcc -c -frepo $(CPPFLAGS) $^ -o $@

lowlevel.cc: b21r.i 
	swig -python -I$(INCLUDE) -c++ -o $@ $<

#*******************************************************
#*************** Dependencies and Objects **************
#*******************************************************

obj/%.o : src/%.cpp
	gcc $(CPPFLAGS) -o $@ -c $< 

.PHONY: FORCE
FORCE:

clean ::
	rm -f obj/* || true
	rm -f *.so *.o *.cc *.rpo *.pyc lowlevel.py

