CC = g++
FILES = bt848grab.o Camera.o BT848.o

bt848grab : $(FILES)
	$(CC) $(FILES) -o $@

%.o : %.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $< 

clean : 
	rm *~ *.o | true

cleanall :
	rm *~ *.o bt848grab | true