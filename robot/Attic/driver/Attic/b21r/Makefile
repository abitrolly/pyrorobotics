VPATH = include:obj:src

include ../../../Makefile.cfg
include ../../../Makefile.src

INCLUDE = $(MOBILITY_INC) -Iinclude

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

B21R_OBJS = obj/B21R.o obj/loadable_B21R.o obj/Sonar.o \
	obj/Laser.o obj/Tactile.o obj/Robot.o obj/Sensor.o obj/Vector.o

# The makefile also needs the following enviroment variables:
# $SAPHIRA, $MOBILITY_ROOT, $MOBILITY_TOOLS

#*******************************************************
#*************** These are the main targets ************
#*******************************************************

b21r : _b21r.so

_lowlevel.so: lowlevel.o obj/b21r.o $(B21R_OBJS) 
	$(CC) $(CPPFLAGS) -shared $^ $(SAPHIRA_LIB) $(LIBDIRS) -o $@ $(LIBS) -lomnithread -L /usr/local/mobility-b-1.1.7-rh6.0/tools/lib -L/usr/local/mobility-b-1.1.7-rh6.0/lib/ -lmby -lomniORB2 -ltcpwrapGK -lmbybase -lIIW -lNMEA -lidlmby -lmbybxxbase -lmbycfr -lmbyserial -lmbyuser -lrFlex3 -lreflex -lreflex -lomniDynamic2 -lomniLC

lowlevel.o: lowlevel.cc
	gcc -c -frepo $(CPPFLAGS) $^ -o $@

lowlevel.cc: b21r.i 
	swig -python -I$(INCLUDE) -c++ -o $@ $<

#*******************************************************
#*************** Dependencies and Objects **************
#*******************************************************

obj/%.o : src/%.cpp
	gcc $(CPPFLAGS) -o $@ -c $< 

#*******************************************************
#*************** Documentation  ************************
#*******************************************************

bin/testrobot: obj/testrobot.o $(B21R_OBJS)
	gcc $(CPPFLAGS) -Lobj -o bin/testrobot obj/testrobot.o $(B21R_OBJS) $(LIBS) $(MOBILITY_LIB)

#*******************************************************
#***************** The Robots & XRCL *******************
#*******************************************************

robots/B21R.rob: $(B21R_OBJS) 
	ld -shared -E $(B21R_OBJS)    $(LIBS) $(MOBILITY_LIB) -o robots/B21R.rob 

.PHONY: FORCE
FORCE:

#*******************************************************
#***************** The Installtion ********************
#*******************************************************

bindir = ${prefix}/bin
datadir = ${prefix}

install: mkinstalldir installall

mkinstalldir: 
		install -d ${prefix} -m 755 
		install -d ${bindir} -m 755 
		install -d ${datadir} -m 755 
#		install -d ${includedir} -m 755 
		install -d ${datadir}/docs -m 755;
		install -d ${datadir}/include -m 755;
		install -d ${datadir}/examples -m 755
		install -d ${datadir}/lib -m 755
		install -d ${datadir}/robots -m 755
		install -d ${datadir}/behaviors -m 755
		install -d ${datadir}/worlds -m 755
#		ln -sf ${includedir} ${datadir}/include

installall:
		INSTALL_INC=`find $(XRCL_INC) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_DOC=`find $(XRCL_DOC) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_BIN=`find $(XRCL_BIN) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_EX=`find $(XRCL_EX) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_LIB=`find $(XRCL_LIB) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_ROB=`find $(XRCL_ROB) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_BEH=`find $(XRCL_BEH) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		INSTALL_WLD=`find $(XRCL_WLD) -path "*RCS*" -prune -o -type d -o -printf "%p "`; \
		for include in $$INSTALL_INC; do \
		echo "Installing $$include to ${datadir}/include"; \
		install -c -m 644 $$include ${datadir}/include; \
		done; \
		for doc in $$INSTALL_DOC; do \
		echo "Installing $$doc to ${datadir}/docs"; \
		install -c -m 644 $$doc ${datadir}/docs; \
		done; \
		for bin in $$INSTALL_BIN; do \
		echo "Installing $$bin to ${bindir}"; \
		install -c -m 755 $$bin ${bindir}; \
		done; \
		for example in $$INSTALL_EX; do \
		echo "Installing $$example to ${datadir}/examples"; \
		install -c -m 644 $$example ${datadir}/examples; \
		done; \
		for lib in $$INSTALL_LIB; do \
		echo "Installing $$lib to ${datadir}/lib"; \
		install -c -m 644 $$lib ${datadir}/lib; \
		done; \
		for robot in $$INSTALL_ROB; do \
		echo "Installing $$robot to ${datadir}/robots"; \
		install -c -m 644 $$robot ${datadir}/robots; \
		done; \
		for behavior in $$INSTALL_BEH; do \
                echo "Installing $$behavior to ${datadir}/behaviors"; \
                install -c -m 644 $$behavior ${datadir}/behaviors; \
                done; \
		for world in $$INSTALL_WLD; do \
		echo "Installing $$world to ${datadir}/worlds"; \
		install -c -m 644 $$world ${datadir}/worlds; \
		done ;

clean ::
	rm -f obj/*.o || true
	rm -f obj/*.a || true
	rm -f robots/*.rob || true
	rm -f *.so *.o *.cc

