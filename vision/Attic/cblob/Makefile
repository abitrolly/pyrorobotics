SO = .so
OBJS = blob.o hsbrgb.o

include ../../Makefile.cfg
include ../../Makefile.src

INC = -I ../../camera/v4l/

all:: _blob$(SO) _hsbrgb$(SO)

%module.c : %.i %.h
	swig -python -o $@ $<

%module.o : %module.c 
	$(CC) -c $(INC) $(PYTHON_INCLUDE) -o $@ $<

_%$(SO) : %module.o %.o
	$(CC) -nodefaultlibs -nostdlib -shared -o $@ $< $(OBJS)

#blob$(SO): $(OBJS)
#	$(LD) -shared $(OBJS) $(INC) -o blob$(SO)

hsbrgb.o: hsbrgb.c hsbrgb.h
	$(CC) $(CFLAGS) $(INC) -c hsbrgb.c -o hsbrgb.o

blob.o: blob.c blob.h hsbrgb.h
	$(CC) $(CFLAGS) $(INC) -c blob.c -o blob.o

clean::
	$(RM) blob$(SO) *module.c _*$(SO) *.o *.pyc 
