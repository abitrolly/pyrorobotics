#ifndef __FAKE_H__
#define __FAKE_H__

#include "../vision/Vision.h"

class Fake : public Vision {

 public:
  Fake(char filename[]);
  void updateMMap(char filename[]);
};

#endif
