CPPFLAGS = -I include
OBJS = obj/BT848.o obj/Camera.o  obj/Blob.o obj/snapshot.o

obj/%.o : src/%.cpp
	gcc $(CPPFLAGS) -o $@ -c $< 

snapshot: $(OBJS)
	gcc  $(OBJS) -o snapshot

clean:
	rm -rf obj/* 
