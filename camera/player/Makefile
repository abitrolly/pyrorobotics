OBJS = _playercam.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../device/ -I/usr/local/include
CPPFLAGS = -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)
#PLAYER_SRC= /root/pyro-install/player
PLAYER_SRC=/home/dblank/playerstage/player
LIBS= -lstdc++ -ldl -L/usr/local/lib -L/usr/lib -lpthread -lplayerpacket -lplayerc -ljpeg -lplayercclient -L/usr/lib/python2.3/config/ -lpython2.3

../device/Device.o: ../device/Device.h ../device/Device.cpp
	cd ../device/; make

_playercam.so: playercam.o PlayerCam.o
	$(CC) $(CPPFLAGS) -shared playercam.o PlayerCam.o ../device/Device.o $(PLAYER_SRC)/client_libs/libplayerpacket/jpeg.o -o $@ $(LIBS)

PlayerCam.o: PlayerCam.cpp PlayerCam.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c PlayerCam.cpp

PlayerCam.cc: PlayerCam.i PlayerCam.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o PlayerCam.cc PlayerCam.i

playercam.o: PlayerCam.cc 
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) PlayerCam.cc -o $@

clean::
	$(RM) *~ *.so *.o PlayerCam.cc playercam.py

