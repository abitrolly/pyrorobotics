SO = .so
OBJS = blob.o hsbrgb.o

include ../../Makefile.cfg

blob$(SO): $(OBJS)
	$(LD) -shared $(OBJS) -o blob$(SO)

hsbrgb.o: hsbrgb.c hsbrgb.h
	$(CC) $(CFLAGS) -c hsbrgb.c -o hsbrgb.o

blob.o: blob.c blob.h hsbrgb.h
	$(CC) $(CFLAGS) -c blob.c -o blob.o

cleanall:
	$(RM) blob$(SO) *.o
