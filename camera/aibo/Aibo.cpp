#include "Aibo.h"

//int socket(int domain, int type, int protocol);

PyObject *Aibo::updateMMap() {
  // get an image from socket
  return PyInt_FromLong(0L);
}

Aibo::Aibo(char *hostname) {
  host = hostname;
  he = gethostbyname(host);
  int PORT = 80;
  // open socket
  server_addr.sin_family = AF_INET;      /* host byte order */
  server_addr.sin_port = htons(PORT);    /* short, network byte order */
  server_addr.sin_addr = *((struct in_addr *)he->h_addr);
  bzero(&(server_addr.sin_zero), 8);     /* zero the rest of the struct */
  if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
    printf("Error: socket could not be opened\n");
  }
  if (connect(sockfd, (struct sockaddr *)&server_addr,
	      sizeof(struct sockaddr)) == -1) {
    printf("Error: socket could not connect\n");    
  }
  // get image details
  char buf[1024];
  send(sockfd, "get\n", 4, 0);
  int numbytes=recv(sockfd, buf, 1024, 0);
  printf(buf);
  width = 100;
  height = 100;
  depth = 3;
  initialize(width, height, depth, 0, 1, 2);
}


