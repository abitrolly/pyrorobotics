#include "B21R.h"

#ifdef __cplusplus
extern "C" {
#endif
  Robot * Robot_0(int argv, char **argc);
#ifdef __cplusplus
}
#endif

Robot * Robot_0(int argc, char **argv) {
  return (new B21R(argc, argv));
}
