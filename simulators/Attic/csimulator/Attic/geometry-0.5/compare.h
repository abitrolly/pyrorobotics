#ifndef TOLERANCE
#define TOLERANCE  .0001
#endif

#define toleq(a,b) ((((a) - TOLERANCE) < (b)) && (((a) + TOLERANCE) > (b)))

