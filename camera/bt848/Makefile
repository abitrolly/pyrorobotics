OBJS = bt848grab.o Camera.o BT848.o
CLEAN = bt848grab
CC = g++

bt848grab: $(OBJS)
	$(CC) $(OBJS) -o $@

include ../../Makefile.cfg
include ../../Makefile.src

%.o: %.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $< $(LIBS)
