# author: Douglas Blank

OBJS = low_videomodule.o low_video.o

include ../../../Makefile.src

low_videomodule.so : low_videomodule.o low_video.o
	ld -shared $^  -o $@

low_videomodule.o : low_videomodule.c
	gcc -c $(PYTHON_INCLUDE) $< -o $@

low_videomodule.c : low_video.i low_video.h
	swig -python -o $@ $<

low_video.o : low_video.c low_video.h
	gcc -c $< -o $@
