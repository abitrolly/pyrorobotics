VPATH = include:obj:src

# The makefile also needs the following enviroment variables:
# $SAPHIRA, $MOBILITY_ROOT, $MOBILITY_TOOLS

#*******************************************************
#*************** These are the main targets ************
#*******************************************************

b21r : robots/B21R.rob 

bin/testrobot: obj/testrobot.o $(B21R_OBJS)
	gcc $(CPPFLAGS) -Lobj -o bin/testrobot obj/testrobot.o $(B21R_OBJS) $(LIBS) $(MOBILITY_LIB)

bin/b21r.so: $(B21R_OBJS)
	gcc $(CPPFLAGS) -shared -Lobj -o bin/b21r.so $(B21R_OBJS) $(LIBS) $(MOBILITY_LIB)

#**********************  Plugins

#*******************************************************
#*************** Variables: objects and flags **********
#*******************************************************

Server: obj/Server.o
	gcc $(CPPFLAGS) -rdynamic -o bin/Server obj/Server.o $(LIBS)

Client: obj/Client.o
	gcc $(CPPFLAGS) -rdynamic -o bin/Client obj/Client.o $(LIBS)

#XRCL_OBJS = 

#obj/RWLock.o  

# obj/Motion.o

# misc: obj/Meteor.o

B21R_OBJS = obj/B21R.o obj/loadable_B21R.o obj/Sonar.o \
	obj/Laser.o obj/Tactile.o obj/Robot.o obj/Sensor.o obj/Vector.o

SIMBOT_OBJS = obj/SimBot.o obj/loadable_SimBot.o \
	obj/SimSonar.o obj/SimLaser.o

PIONEER_OBJS = obj/Pioneer.o obj/loadable_Pioneer.o obj/PioneerSonar.o obj/Sensor.o


LIBS  = -lpthread -ldl -lc -lm  -lpthread -lncurses
MOBILITY_LIB = -L$(MOBILITY_ROOT)/lib -L$(MOBILITY_TOOLS)/lib \
	-lmby -lidlmby -lomniDynamic2 -lomniORB2 -ltcpwrapGK -lomnithread 
MOBILITY_INC = -I$(MOBILITY_ROOT)/include -I$(MOBILITY_TOOLS)/include
SAPHIRA_LIB = -L$(SAPHIRA)/handler/obj -L${XRCL_HOME}/lib -lsfx -lptzsys
SAPHIRA_INC = -I$(SAPHIRA)/handler/include
QT_LIB = -L$(QT_DIR)/lib -lqt
QT_INC =  -I$(QT_DIR)/include

CPPFLAGS = -Wall -Wno-unused -DNTSC -D_POSIX_THREADS -D_POSIX_THREAD_SAFE_FUNCTIONS \
	-DXRCL_VER=$(XRCL_VER) -D_REENTRANT -DPOSIX -D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -D USINGTHREADS -DLINUX -D_GNU_SOURCE\
	$(QT_INC) $(MOBILITY_INC) $(SAPHIRA_INC) -Iinclude -g


#*******************************************************
#*************** Dependencies and Objects **************
#*******************************************************

obj/%.o : src/%.cpp
	gcc $(CPPFLAGS) -o $@ -c $< 

#*******************************************************
#*************** Documentation  ************************
#*******************************************************

documentation: $(XRCL_DOC)/xrcl/book1.html $(XRCL_DOC)/todo.html $(XRCL_DOC)/README\
	$(XRCL_DOC)/index.html $(XRCL_DOC)/ChangeLog

$(XRCL_DOC)/xrcl/book1.html : docs/xrcl.sgml
	cd docs; db2html xrcl.sgml; 
	rm -rf $(XRCL_DOC)/xrcl
	mv -f docs/xrcl $(XRCL_DOC)
	cd docs;db2ps xrcl.sgml; db2pdf xrcl.sgml
	mv -f docs/xrcl.pdf $(XRCL_DOC)
	mv -f docs/xrcl.ps $(XRCL_DOC)
	rm -rf docs/xrcl stylesheet-images docs/stylesheet-images docs/xrcl.junk
	rm -f docs/xrcl.ps docs/xrcl.pdf docbook.css docs/docbook.css
	rm -f docs/xrcl.tex docs/xrcl.log docs/xrcl.aux docs/xrcl.dvi

$(XRCL_DOC)/index.html: docs/index.html behaviors/Patrol.xrcl
	cp docs/index.html $(XRCL_DOC)
	cp behaviors/Patrol.xrcl $(XRCL_DOC)

$(XRCL_DOC)/README: README
	cp README $(XRCL_DOC)

$(XRCL_DOC)/todo.html: docs/todo.sgml
	cd docs; dbnochunks todo.sgml
	mv -f docs/todo.html $(XRCL_DOC)
	rm -f docs/docbook.css docs/docbook.css docs/todo.log

#*******************************************************
#********************* MOC files ***********************
#*******************************************************

include/Video.moc : include/Video.h src/Video.cpp
	$(QT_MOC) include/Video.h -o include/Video.moc

include/gui-X11.moc : include/gui-X11.h src/gui-X11.cpp
	$(QT_MOC) include/gui-X11.h -o include/gui-X11.moc

include/Editor.moc : include/Editor.h src/Editor.cpp
	$(QT_MOC) include/Editor.h -o include/Editor.moc

#*******************************************************
#***************** The Robots & XRCL *******************
#*******************************************************

robots/B21R.rob: $(B21R_OBJS) 
	ld -shared -E $(B21R_OBJS)    $(LIBS) $(MOBILITY_LIB) -o robots/B21R.rob 

robots/SimBot.rob : $(SIMBOT_OBJS)
	ld -shared -E $(SIMBOT_OBJS) $(LIBS) -o robots/SimBot.rob

robots/Pioneer.rob : $(PIONEER_OBJS)
	ld -shared -E $(PIONEER_OBJS) $(LIBS) $(SAPHIRA_LIB) -o robots/Pioneer.rob

# obj/libvis.a 
bin/xrcl : $(XRCL_OBJS) 
	gcc $(CPPFLAGS) -Lobj -rdynamic -o bin/xrcl $(XRCL_OBJS) $(LIBS) $(SAPHIRA_LIB) $(QT_LIB) 

obj/gui-X11.o: Makefile     #This is in order to rebuild when we change the version

#obj/libvis.a:	FORCE # added by SBM
#	$(MAKE) -C src/visualize
#	ar r obj/libvis.a src/visualize/*.o

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

clean :
	rm -f obj/*.o || true
	rm -f obj/*.a || true
	rm -f robots/*.rob || true
	rm -f behaviors/*.beh || true
	rm -f bin/xrcl || true
	rm -f obj/*.moc || true
	rm -f plugins/*.so || true
	$(MAKE) clean -C src/visualize

