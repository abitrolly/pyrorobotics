OBJS = array3dmodule.o Matrix.o Canvas3D.o
INC = -DHAVE_NUMPY -DHAVE_NUMERIC_ARRAYOBJECT_H -D__cplusplus
LIBS = -lm 

include ../../Makefile.src

array3dmodule.so : $(OBJS)
	gcc -shared $(OBJS) -o array3dmodule.so $(LIBS)

array3dmodule.o : array3dmodule.cpp
	gcc $(INC) -c $(PYTHON_INCLUDE) array3dmodule.cpp -o array3dmodule.o

#array3dmodule.cpp : array3d.i array3d.h
#	swig -python -c++ -o array3dmodule.cpp array3d.i

#array3d.o : array3d.c array3d.h
#	gcc $(INC) -c $(PYTHON_INCLUDE) array3d.c -o array3d.o

Matrix.o : Matrix.cpp
	gcc $(INC) -c $(PYTHON_INCLUDE) Matrix.cpp -o Matrix.o

Canvas3D.o : Canvas3D.cpp
	gcc $(INC) -c $(PYTHON_INCLUDE) Canvas3D.cpp -o Canvas3D.o

#draw_in_array.o : draw_in_array.cpp draw_in_array.h
#	gcc $(INC) draw_in_array.cpp -c $(PYTHONINCLUDE) -o draw_in_array.o

