#include "Saphira.h"

#include <stdio.h>

main() {
  Saphira s;
  s.Connect();
  while(1) {
    printf("Robot position: (%f, %f)\n", s.getX(), s.getY());
    printf("Sonar 0: (%f, %f) at %f\n", s.getSonarXCoord(0), s.getSonarYCoord(0), s.getSonarRange(0));
    if (s.getSonarRange(0) < 1.0) {
      s.Move(1, 1);
    } else {
      s.Move(0, 0);
    }
    s.UpdatePosition();
  }
}
