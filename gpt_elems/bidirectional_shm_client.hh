#ifndef BIDIRECTIONAL_SHM_CLIENT_h
#define BIDIRECTIONAL_SHM_CLIENT_h 1

extern "C" {
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <semaphore.h>
#include <sys/mman.h>
}

#include "shm_structs.hh"
#include <string>

using namespace std;

class bidirectional_shm_client {

public:
  bidirectional_shm_client();
  ~bidirectional_shm_client();
  int scatterParticle(myParticleInfo *in, myParticleInfo *out);

private:
  struct shared_memory {
	char buf[256];
	int flag; //for possible future use
  };
  
  
  shared_memory *send_shared_mem_ptr, *resp_shared_mem_ptr;
  sem_t *send_sem, *resp_sem, *sem_send_mutex, *sem_resp_mutex;
  int fd_send_shm, fd_resp_shm;

  void error (string msg);
};


#endif
