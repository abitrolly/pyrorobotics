#include "Canvas3D.h"

#define SWIGPYTHON
/***********************************************************************
 * common.swg
 *
 *     This file contains generic SWIG runtime support for pointer
 *     type checking as well as a few commonly used macros to control
 *     external linkage.
 *
 * Author : David Beazley (beazley@cs.uchicago.edu)
 *
 * Copyright (c) 1999-2000, The University of Chicago
 * 
 * This file may be freely redistributed without license or fee provided
 * this copyright message remains intact.
 ************************************************************************/

#include <string.h>

#if defined(_WIN32) || defined(__WIN32__)
#       if defined(_MSC_VER)
#               if defined(STATIC_LINKED)
#                       define SWIGEXPORT(a) a
#               else
#                       define SWIGEXPORT(a) __declspec(dllexport) a
#               endif
#       else
#               if defined(__BORLANDC__)
#                       define SWIGEXPORT(a) a _export
#               else
#                       define SWIGEXPORT(a) a
#       endif
#endif
#else
#       define SWIGEXPORT(a) a
#endif

#ifdef SWIG_GLOBAL
#define SWIGRUNTIME(a) SWIGEXPORT(a)
#else
#define SWIGRUNTIME(a) static a
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct swig_type_info {
  char  *name;                 
  void *(*converter)(void *);
  char  *str;
  struct swig_type_info  *next;
  struct swig_type_info  *prev;
} swig_type_info;

#ifdef SWIG_NOINCLUDE
SWIGEXPORT(swig_type_info *) SWIG_TypeRegister(swig_type_info *);
SWIGEXPORT(swig_type_info *) SWIG_TypeCheck(char *c, swig_type_info *);
SWIGEXPORT(void *) SWIG_TypeCast(swig_type_info *, void *);
#else

static swig_type_info *swig_type_list = 0;

/* Register a type mapping with the type-checking */
SWIGRUNTIME(swig_type_info *)
SWIG_TypeRegister(swig_type_info *ti)
{
  swig_type_info *tc, *head, *ret, *next;
  /* Check to see if this type has already been registered */
  tc = swig_type_list;
  while (tc) {
    if (strcmp(tc->name, ti->name) == 0) {
      /* Already exists in the table.  Just add additional types to the list */
      head = tc;
      next = tc->next;
      goto l1;
    }
    tc = tc->prev;
  }
  head = ti;
  next = 0;

  /* Place in list */
  ti->prev = swig_type_list;
  swig_type_list = ti;

  /* Build linked lists */
 l1:
  ret = head;
  tc = ti + 1;
  /* Patch up the rest of the links */
  while (tc->name) {
    head->next = tc;
    tc->prev = head;
    head = tc;
    tc++;
  }
  head->next = next;
  return ret;
}

/* Check the typename */
SWIGRUNTIME(swig_type_info *) 
SWIG_TypeCheck(char *c, swig_type_info *ty)
{
  swig_type_info *s;
  if (!ty) return 0;        /* Void pointer */
  s = ty->next;             /* First element always just a name */
  while (s) {
    if (strcmp(s->name,c) == 0) {
      if (s == ty->next) return s;
      /* Move s to the top of the linked list */
      s->prev->next = s->next;
      if (s->next) {
	s->next->prev = s->prev;
      }
      /* Insert s as second element in the list */
      s->next = ty->next;
      if (ty->next) ty->next->prev = s;
      ty->next = s;
      return s;
    }
    s = s->next;
  }
  return 0;
}

/* Cast a pointer (needed for C++ inheritance */
SWIGRUNTIME(void *) 
SWIG_TypeCast(swig_type_info *ty, void *ptr) 
{
  if ((!ty) || (!ty->converter)) return ptr;
  return (*ty->converter)(ptr);
}

/* Search for a swig_type_info structure */
SWIGRUNTIME(void *)
SWIG_TypeQuery(const char *name) {
  swig_type_info *ty = swig_type_list;
  while (ty) {
    if (ty->str && (strcmp(name,ty->str) == 0)) return ty;
    if (ty->name && (strcmp(name,ty->name) == 0)) return ty;
    ty = ty->prev;
  }
  return 0;
}

#endif

#ifdef __cplusplus
}
#endif



/***********************************************************************
 * python.swg
 *
 *     This file contains the runtime support for Python modules
 *     and includes code for managing global variables and pointer
 *     type checking.
 *
 * Author : David Beazley (beazley@cs.uchicago.edu)
 ************************************************************************/

#include <stdlib.h>
#include "Python.h"

#ifdef __cplusplus
extern "C" {
#endif

#define SWIG_PY_INT     1
#define SWIG_PY_FLOAT   2
#define SWIG_PY_STRING  3
#define SWIG_PY_POINTER 4

/* Constant information structure */
typedef struct swig_const_info {
    int type;
    char *name;
    long lvalue;
    double dvalue;
    void   *pvalue;
    swig_type_info **ptype;
} swig_const_info;

#ifdef SWIG_NOINCLUDE

SWIGEXPORT(PyObject *)        SWIG_newvarlink();
SWIGEXPORT(void)              SWIG_addvarlink(PyObject *, char *, PyObject *(*)(void), int (*)(PyObject *));
SWIGEXPORT(int)               SWIG_ConvertPtr(PyObject *, void **, swig_type_info *, int);
SWIGEXPORT(void)              SWIG_MakePtr(char *c, void *, swig_type_info *);
SWIGEXPORT(PyObject *)        SWIG_NewPointerObj(void *, swig_type_info *);
SWIGEXPORT(void)              SWIG_InstallConstants(PyObject *d, swig_const_info constants[]);

#else

/* -----------------------------------------------------------------------------
 * global variable support code.
 * ----------------------------------------------------------------------------- */

typedef struct swig_globalvar {   
  char       *name;                  /* Name of global variable */
  PyObject *(*get_attr)(void);       /* Return the current value */
  int       (*set_attr)(PyObject *); /* Set the value */
  struct swig_globalvar *next;
} swig_globalvar;

typedef struct swig_varlinkobject {
  PyObject_HEAD
  swig_globalvar *vars;
} swig_varlinkobject;

static PyObject *
swig_varlink_repr(swig_varlinkobject *v) {
  v = v;
  return PyString_FromString("<Global variables>");
}

static int
swig_varlink_print(swig_varlinkobject *v, FILE *fp, int flags) {
  swig_globalvar  *var;
  flags = flags;
  fprintf(fp,"Global variables { ");
  for (var = v->vars; var; var=var->next) {
    fprintf(fp,"%s", var->name);
    if (var->next) fprintf(fp,", ");
  }
  fprintf(fp," }\n");
  return 0;
}

static PyObject *
swig_varlink_getattr(swig_varlinkobject *v, char *n) {
  swig_globalvar *var = v->vars;
  while (var) {
    if (strcmp(var->name,n) == 0) {
      return (*var->get_attr)();
    }
    var = var->next;
  }
  PyErr_SetString(PyExc_NameError,"Unknown C global variable");
  return NULL;
}

static int
swig_varlink_setattr(swig_varlinkobject *v, char *n, PyObject *p) {
  swig_globalvar *var = v->vars;
  while (var) {
    if (strcmp(var->name,n) == 0) {
      return (*var->set_attr)(p);
    }
    var = var->next;
  }
  PyErr_SetString(PyExc_NameError,"Unknown C global variable");
  return 1;
}

statichere PyTypeObject varlinktype = {
  PyObject_HEAD_INIT(0)              
  0,
  "swigvarlink",                      /* Type name    */
  sizeof(swig_varlinkobject),         /* Basic size   */
  0,                                  /* Itemsize     */
  0,                                  /* Deallocator  */ 
  (printfunc) swig_varlink_print,     /* Print        */
  (getattrfunc) swig_varlink_getattr, /* get attr     */
  (setattrfunc) swig_varlink_setattr, /* Set attr     */
  0,                                  /* tp_compare   */
  (reprfunc) swig_varlink_repr,       /* tp_repr      */    
  0,                                  /* tp_as_number */
  0,                                  /* tp_as_mapping*/
  0,                                  /* tp_hash      */
};

/* Create a variable linking object for use later */
SWIGRUNTIME(PyObject *)
SWIG_newvarlink(void) {
  swig_varlinkobject *result = 0;
  result = PyMem_NEW(swig_varlinkobject,1);
  varlinktype.ob_type = &PyType_Type;    /* Patch varlinktype into a PyType */
  result->ob_type = &varlinktype;
  result->vars = 0;
  result->ob_refcnt = 0;
  Py_XINCREF((PyObject *) result);
  return ((PyObject*) result);
}

SWIGRUNTIME(void)
SWIG_addvarlink(PyObject *p, char *name,
	   PyObject *(*get_attr)(void), int (*set_attr)(PyObject *p)) {
  swig_varlinkobject *v;
  swig_globalvar *gv;
  v= (swig_varlinkobject *) p;
  gv = (swig_globalvar *) malloc(sizeof(swig_globalvar));
  gv->name = (char *) malloc(strlen(name)+1);
  strcpy(gv->name,name);
  gv->get_attr = get_attr;
  gv->set_attr = set_attr;
  gv->next = v->vars;
  v->vars = gv;
}
/* Convert a pointer value */
SWIGRUNTIME(int)
SWIG_ConvertPtr(PyObject *obj, void **ptr, swig_type_info *ty, int flags) {
  unsigned long p;
  register int d;
  swig_type_info *tc;
  char  *c;
  static PyObject *SWIG_this = 0;
  int    newref = 0;

  if (!obj || (obj == Py_None)) {
    *ptr = 0;
    return 0;
  }
#ifdef SWIG_COBJECT_TYPES
  if (!(PyCObject_Check(obj))) {
    if (!SWIG_this)
      SWIG_this = PyString_InternFromString("this");
    obj = PyObject_GetAttr(obj,SWIG_this);
    newref = 1;
    if (!obj) goto type_error;
    if (!PyCObject_Check(obj)) {
      Py_DECREF(obj);
      goto type_error;
    }
  } 
  *ptr = PyCObject_AsVoidPtr(obj);
  c = (char *) PyCObject_GetDesc(obj);
  if (newref) Py_DECREF(obj);
  goto cobject;
#else
  if (!(PyString_Check(obj))) {
    if (!SWIG_this)
      SWIG_this = PyString_InternFromString("this");
    obj = PyObject_GetAttr(obj,SWIG_this);
    newref = 1;
    if (!obj) goto type_error;
    if (!PyString_Check(obj)) {
      Py_DECREF(obj);
      goto type_error;
    }
  } 
  c = PyString_AsString(obj);
  p = 0;
  /* Pointer values must start with leading underscore */
  if (*c != '_') {
    *ptr = (void *) 0;
    if (strcmp(c,"NULL") == 0) {
      if (newref) Py_DECREF(obj);
      return 0;
    } else {
      if (newref) Py_DECREF(obj);
      goto type_error;
    }
  }
  c++;
  /* Extract hex value from pointer */
  while ((d = *c)) {
    if ((d >= '0') && (d <= '9'))
      p = (p << 4) + (d - '0');
    else if ((d >= 'a') && (d <= 'f'))
      p = (p << 4) + (d - ('a'-10));
    else
      break; 
    c++;
  }
  *ptr = (void *) p;
  if (newref) Py_DECREF(obj);
#endif

#ifdef SWIG_COBJECT_TYPES
cobject:
#endif

  if (ty) {
    tc = SWIG_TypeCheck(c,ty);
    if (!tc) goto type_error;
    *ptr = SWIG_TypeCast(tc,(void*)p);
  }
  return 0;

type_error:

  if (flags) {
    if (ty) {
      char *temp = (char *) malloc(64+strlen(ty->name));
      sprintf(temp,"Type error. Expected %s", ty->name);
      PyErr_SetString(PyExc_TypeError, temp);
      free((char *) temp);
    } else {
      PyErr_SetString(PyExc_TypeError,"Expected a pointer");
    }
  }
  return -1;
}

/* Take a pointer and convert it to a string */
SWIGRUNTIME(void) 
SWIG_MakePtr(char *c, void *ptr, swig_type_info *ty) {
  static char hex[17] = "0123456789abcdef";
  unsigned long p, s;
  char result[32], *r; 
  r = result;
  p = (unsigned long) ptr;
  if (p > 0) {
    while (p > 0) {
      s = p & 0xf;
      *(r++) = hex[s];
      p = p >> 4;
    }
    *r = '_';
    while (r >= result)
      *(c++) = *(r--);
    strcpy (c, ty->name);
  } else {
    strcpy (c, "NULL");
  }
}

/* Create a new pointer object */
SWIGRUNTIME(PyObject *)
SWIG_NewPointerObj(void *ptr, swig_type_info *type) {
  char result[512];
  PyObject *robj;
  if (!ptr) {
    Py_INCREF(Py_None);
    return Py_None;
  }
#ifdef SWIG_COBJECT_TYPES
  robj = PyCObject_FromVoidPtrAndDesc((void *) ptr, type->name, NULL);
#else
  SWIG_MakePtr(result,ptr,type);
  robj = PyString_FromString(result);
#endif
  return robj;
}

/* Install Constants */
SWIGRUNTIME(void)
SWIG_InstallConstants(PyObject *d, swig_const_info constants[]) {
  int i;
  PyObject *obj;
  for (i = 0; constants[i].type; i++) {
    switch(constants[i].type) {
    case SWIG_PY_INT:
      obj = PyInt_FromLong(constants[i].lvalue);
      break;
    case SWIG_PY_FLOAT:
      obj = PyFloat_FromDouble(constants[i].dvalue);
      break;
    case SWIG_PY_STRING:
      obj = PyString_FromString((char *) constants[i].pvalue);
      break;
    case SWIG_PY_POINTER:
      obj = SWIG_NewPointerObj(constants[i].pvalue, *(constants[i]).ptype);
      break;
    default:
      obj = 0;
      break;
    }
    if (obj) {
      PyDict_SetItemString(d,constants[i].name,obj);
      Py_DECREF(obj);
    }
  }
}

#endif

#ifdef __cplusplus
}
#endif

#include <sysmodule.h>
#ifdef HAVE_NUMPY
#  if defined(HAVE_ARRAYOBJECT_H)
#    include <arrayobject.h>
#  elif defined(HAVE_EXTESNSIONS_ARRAYOBJECT_H)
#    include <Extensions/arrayobject.h>
#  elif defined(HAVE_NUMERIC_ARRAYOBJECT_H)
#    include <Numeric/arrayobject.h>
#  else
#    error "arrayobject.h not found, but HAVE_NUMPY defined"
#  endif
#endif 

/* -------- TYPES TABLE (BEGIN) -------- */

#define  SWIGTYPE_p_unsigned_char swig_types[0] 
static swig_type_info *swig_types[2];

/* -------- TYPES TABLE (END) -------- */

#define SWIG_init    initarray3d

#define SWIG_name    "array3d"
 
#include"array3d.h"
#ifdef __cplusplus
extern "C" {
#endif

static PyObject *_process(PyObject *self, PyObject *args) {
  PyObject *resultobj;
  PyArrayObject *array = 0;
  PyObject *list = 0, *obj_obj;
  PyObject *list_of_args = 0;
  PyObject *item = 0, *o[10];
  char *buf;
  int obj_code, list_len, a[10], ocnt;
  int n, i, x, y, width, height, rowstride = -1, len, depth;      
  if(!PyArg_ParseTuple(args,"O!O:process", 
		       &PyArray_Type, &array,
		       &list))
    return NULL;
  if (array->descr->type_num != PyArray_UBYTE) {
    PyErr_SetString(PyExc_TypeError, "array data must be unsigned bytes");
    return NULL;
  }
  if (array->nd < 2) {
    PyErr_SetString(PyExc_TypeError, "array must have at least 2 axes");
    return NULL;
  }
  if (!PySequence_Check(list)) {
    PyErr_SetString(PyExc_TypeError, "second arg must be a sequence");
    return NULL;
  }
  if (array->nd == 2 || array->nd == 3 && array->dimensions[2] == 1) { 
    if (array->strides[1] != 1) {
      PyErr_SetString(PyExc_TypeError, "second axis must be contiguous");
      return NULL;
    }
    //    gdk_draw_gray_image(PyGdkWindow_Get(drawable), PyGdkGC_Get(gc), x, y,
    //width, height, dith, buf, rowstride);
  } else if (array->nd == 3 && array->dimensions[2] == 3) {
    if (array->strides[1] != 3) {
      PyErr_SetString(PyExc_TypeError, "second axis must be contiguous");
      return NULL;
    }
    //  gdk_draw_rgb_image(PyGdkWindow_Get(drawable), PyGdkGC_Get(gc), x, y,
    //width, height, dith, buf, rowstride);
  } else if (array->nd == 3 && array->dimensions[2] == 4) {
    if (array->strides[1] != 4) {
      PyErr_SetString(PyExc_TypeError, "second axis must be contiguous");
      return NULL;
    }
    //gdk_draw_rgb_32_image(PyGdkWindow_Get(drawable), PyGdkGC_Get(gc), x, y,
    //width, height, dith, buf, rowstride);
  } else {
    PyErr_SetString(PyExc_TypeError,
		    "array must be MxN or MxNxP where P is 1, 3 or 4");
    return NULL;
  }
  // ok we made it through tests, let's process the list
  n = PySequence_Length(list);  
  width = array->dimensions[1];
  height = array->dimensions[0];
  depth = array->dimensions[2];
  buf = (char *)array->data;
  rowstride = array->strides[0];
  printf("array3d: w = %d h = %d buf = (%p) stride = %d n = %d\n",
	 (int) width,
	 (int) height,
	 buf,
	 (int) rowstride, n);
  // canvas:
  Canvas3D canvas(width, height, buf, rowstride);
  int centerx = width/2,centery = height/2;
  // should be in an onresize function 
  canvas.SetSize(width +2, height+2 );

  // clipping stuff
  Vertex3D VertsIn[3],VertsOut[180],point;
  long lVertCount;
  PolygonHolder * polygon = NULL;
  //  PolygonList.SetSize(0L,500L);
  
  // matrix stack information
  const int MaxStackSize = 15;
  static Matrix MatrixStack[MaxStackSize];
  int StackTop = 0;
  
  Matrix matrix;
  
  // draw a grid here

  matrix = 
    // move away from the screen
    Matrix::Translate(0,0,-75.0) *  
    // do the screen rotate
    //(pfROBOTVIEW ? RotateMatrixRobot : RotateMatrixWorld) * 
    // this will let the robot rotate the world
    //(pref_view == pfROBOTVIEW ?
    Matrix::RotateZRad(-1.0) * //-__Robot->getActualRadth()) :
    // This will point 0 angle of world, up
    //Matrix::RotateZRad(-PI/2)* 
    // tip down a bit:
    Matrix::RotateYDeg(50) * //) *
    // scale it
    Matrix::Scale(10,10,10);	

  for (i = 0; i < n; i++) {
    item = PySequence_GetItem(list, i); // car
    Py_DECREF(item);
    if (!PySequence_Check(item)) {
      PyErr_SetString(PyExc_TypeError, "sequence member must be an seq");
      return NULL;
    }
    list_len = PySequence_Length(item);  
    if (list_len > 0) {
      obj_obj = PySequence_GetItem(item, 0); // car of command
      Py_DECREF(obj_obj);
      obj_code = (int) PyInt_AsLong(obj_obj);
      printf("   obj_code item = %d\n", obj_code);
      for (ocnt = 0; ocnt < (list_len - 1); ocnt++) {
	o[ocnt] = PySequence_GetItem(item, ocnt + 1); // x, y, colors, etc
	Py_DECREF(o[ocnt]);
	a[ocnt] = (int) PyInt_AsLong(o[ocnt]);
      }

      // DRAW DATA:
      switch (obj_code) {
      case Canvas3D::LINE: // Draw line
	if (list_len != 7) {
	  PyErr_SetString(PyExc_TypeError, "line needs 6 values");
	  return NULL;
	}
	VertsIn[0] = matrix 
	  * Matrix::Translate(0,0,0)    //-__Robot->getActualX(),
	  // -__Robot->getActualY(),0)
	  * Vertex3D(
		     a[0],
		     a[1],
		     a[2]
		     );
	VertsIn[1] = matrix 
	  * Matrix::Translate(0, 0,0 ) // -__Robot->getActualX(),
	  // -__Robot->getActualY(),0)
	  * Vertex3D(
		     a[3],
		     a[4],
		     a[5]
		     );
	
	canvas.ClipFace(VertsIn,2,VertsOut,lVertCount);
	if (!lVertCount)
	  break;
	
	canvas.AddPerspective(VertsOut[0]);
	canvas.AddPerspective(VertsOut[1]);
	
	canvas.draw_line(
			 centerx+(int)VertsOut[0].x, 
			 centery-(int)VertsOut[0].y,
			 centerx+(int)VertsOut[1].x,
			 centery-(int)VertsOut[1].y
			 );
	canvas.fill(
		    centerx+(int)VertsOut[0].x, 
		    centery-(int)VertsOut[0].y);
	break;
      case Canvas3D::LINE_WIDTH:
	canvas.line_width = a[0];
	break;
      case Canvas3D::POINT:
	if (list_len != 4) {
	  PyErr_SetString(PyExc_TypeError, "point needs 3 values");
	  return NULL;
	}
	VertsIn[0] = matrix 
	  * Matrix::Translate(0,0,0)    //-__Robot->getActualX(),
	  // -__Robot->getActualY(),0)
	  * Vertex3D(
		     a[0],
		     a[1],
		     a[2]
		     );
	canvas.ClipFace(VertsIn,1,VertsOut,lVertCount);
	if (!lVertCount)
	  break;
	
	canvas.AddPerspective(VertsOut[0]);
	
	canvas.draw_point(
			 centerx+(int)VertsOut[0].x, 
			 centery-(int)VertsOut[0].y
			 );
	break;
      case Canvas3D::COLOR:
	if (list_len != 4) {
	  PyErr_SetString(PyExc_TypeError, "color needs 3 values");
	  return NULL;
	}
	canvas.red = a[0];
	canvas.green = a[1];
	canvas.blue = a[2];
	break;
      default:
	PyErr_SetString(PyExc_TypeError, "obj_code error in array3d");
	return NULL;
      }
    }
  }
  Py_INCREF(Py_None);
  resultobj = Py_None;
  return resultobj;
}

static PyMethodDef array3dMethods[] = {
	 { "process", _process, METH_VARARGS },
	 { NULL, NULL }
};

#ifdef __cplusplus
}
#endif

/* -------- TYPE CONVERSION AND EQUIVALENCE RULES (BEGIN) -------- */

static swig_type_info _swigt__p_unsigned_char[] = {{"_p_unsigned_char", 0, "unsigned char *"},{"_p_unsigned_char"},{0}};

static swig_type_info *swig_types_initial[] = {
_swigt__p_unsigned_char, 
0
};


/* -------- TYPE CONVERSION AND EQUIVALENCE RULES (END) -------- */

static swig_const_info swig_const_table[] = {
{0}};

static PyObject *SWIG_globals;
#ifdef __cplusplus
extern "C" 
#endif
SWIGEXPORT(void) initarray3d(void) {
    PyObject *m, *d;
    int i;
    SWIG_globals = SWIG_newvarlink();
    m = Py_InitModule("array3d", array3dMethods);
    d = PyModule_GetDict(m);
#ifdef HAVE_NUMPY
    import_array();
#endif        
    for (i = 0; swig_types_initial[i]; i++) {
      swig_types[i] = SWIG_TypeRegister(swig_types_initial[i]);
    }
    SWIG_InstallConstants(d,swig_const_table);
}

