#ifndef __AIBO_H__
#define __AIBO_H__

#include <sys/types.h> 
#include <netinet/in.h> 
#include <netdb.h>
#include <sys/socket.h> 
#include "Device.h"

class Aibo : public Device {
 public:
  Aibo(char *hostname);
  PyObject *updateMMap();
  char *host;
  int sockfd;
 private:
  struct sockaddr_in server_addr;
  struct hostent *he;
};

#endif
