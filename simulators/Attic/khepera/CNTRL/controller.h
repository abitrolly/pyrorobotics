#ifndef CONTROLLER_H
#define CONTROLLER_H


#include <sys/types.h>

#define SHM_BUF_SIZE  64
#define SHM_KEY_IN    (key_t) 4001
#define SHM_KEY_OUT   (key_t) 4000
#define SHM_PERM      0600


struct cntrl {
	int shmid_in, shmid_out;
	char *shm_in, *shm_out;
};

extern struct cntrl *initControl(void);
extern char *sendMessage(struct cntrl *control, char *message);


#endif
