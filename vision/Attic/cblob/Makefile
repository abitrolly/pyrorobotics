SO = .so
OBJS = blob.o hsbrgb.o

include ../../Makefile.cfg

INC = -I ../../camera/v4l/

blob$(SO): $(OBJS)
	$(LD) -shared $(OBJS) $(INC) -o blob$(SO)

hsbrgb.o: hsbrgb.c hsbrgb.h
	$(CC) $(CFLAGS) $(INC) -c hsbrgb.c -o hsbrgb.o

blob.o: blob.c blob.h hsbrgb.h
	$(CC) $(CFLAGS) $(INC) -c blob.c -o blob.o

cleanall:
	$(RM) blob$(SO) *.o
