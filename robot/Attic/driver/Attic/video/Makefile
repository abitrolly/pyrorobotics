PYTHONINCLUDE= -I/usr/local/include/python2.0 -I/usr/local/lib/python2.0/config


low_videomodule.so : low_videomodule.o low_video.o
	ld -shared $^  -o $@

low_videomodule.o : low_videomodule.c
	gcc -c $(PYTHONINCLUDE) $< -o $@

low_videomodule.c : low_video.i low_video.h
	swig -python -o $@ $<

low_video.o : low_video.c low_video.h
	gcc -c $< -o $@


clean:
	rm -f *.o *.so *module.c