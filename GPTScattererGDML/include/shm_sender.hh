/**
   Send a character string over shared memory
 */

#ifndef shm_sender_h
#define shm_sender_h 1


extern "C" {
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <semaphore.h>
#include <sys/mman.h>
#include <string.h>
}

#include "shm_structs.hh"

#include <string>
using namespace std;


class  shm_sender {
public:
  shm_sender(string mutex_sem_name, string sem_name, string shm_name);
  ~shm_sender();

  void send(char* msg);
  void send(const myParticleInfo *info);

private:
  void errormsg(string msg);

  struct shared_memory {
	char buf[256];
	int flag; //for possible future use
  };

  shared_memory *send_shared_mem_ptr;
  int fd_send_shm;

  sem_t *send_sem, *sem_send_mutex;

};

#endif
