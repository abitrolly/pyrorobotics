#include <ctype.h>
#include "BT848.h"


#define TRUE   1
#define FALSE  0

int str_to_int(char *input, int *target);

main(int argc, char *argv[]) {
  int ncols, nrows;
  char filename[255];
  if (argc <= 1) {
    printf("Call with filename\n");
    exit(1);
  }
  strcpy(filename, argv[1]);
  if(argc==4) {
    str_to_int(argv[2], &ncols);
    str_to_int(argv[3], &nrows);
  } else {
    ncols = ICOLS;
    nrows = IROWS;
  }
  printf("%d, %d\n", ncols, nrows);
  BT848 *cam = new BT848( "/dev/bt848fg0", ncols, nrows );
  cam->Update();
  cam->Update();
  cam->Update();
  cam->saveFile(filename);
}


int str_to_int(char *input, int *target) {
  int digit, total = 0, sign, length, valid = TRUE, i, j;

  length = strlen(input);
  
  if( *input == '-' ) {
    sign = -1;
    length -= 1;
    input++;
  } else {
    sign = 1;
  }
  for( i = length - 1; i >= 0; i-- ) {
    if( !isdigit(*(input + i)) ) { valid = FALSE;  break; }
    digit = (int) (*(input + i) - '0');
    for( j = i + 1; j < length; j++ )  digit *= 10;
    total += digit;
  }
  if( valid ) {
    *target = (sign*total);
    return 0;
  } else return -1;
}
