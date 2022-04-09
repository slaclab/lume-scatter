
#include "shm_sender.hh"
#include "shm_structs.hh"

// Print system error and exit
void shm_sender::errormsg (std::string msg) {
  string classStr =  "shm_sender::";
  perror ( (classStr + msg).c_str());
  exit (1);
}


shm_sender::shm_sender(string mutex_sem_name, string sem_name, string shm_name)
{
  //  mutual exclusion semaphore, mutex_sem with an initial value 0.
  if ((sem_send_mutex = sem_open(mutex_sem_name.c_str(), O_CREAT, 0660, 0)) == SEM_FAILED)
	this->errormsg ("sem_open mutex_sem_name");

  //shared memory semaphore
  if ((send_sem = sem_open(sem_name.c_str(), O_CREAT, 0660, 0)) == SEM_FAILED)
	this->errormsg ("sem_open");

    // Get shared memory 
  if ((fd_send_shm = shm_open(shm_name.c_str(), O_RDWR | O_CREAT | O_EXCL, 0660)) == -1)
	this->errormsg("shm_open");

  if (ftruncate(fd_send_shm, sizeof (struct shared_memory)) == -1)
	this->errormsg ("ftruncate");

  if ((send_shared_mem_ptr = (shared_memory *) mmap(NULL, sizeof (struct shared_memory), PROT_READ | PROT_WRITE, MAP_SHARED,
								   fd_send_shm, 0)) == MAP_FAILED)
	this->errormsg("send mmap");
}

shm_sender::~shm_sender() {
  if (munmap (send_shared_mem_ptr, sizeof (struct shared_memory)) == -1) {
	errormsg("munmap");
  }
}

// send msg over the shared memory
void shm_sender::send(char* msg) {

  // Wait for shm to become available for writing(the corresponding semaphore is > 0)
  if (sem_wait(sem_send_mutex) == -1) {
	this->errormsg("sem_wait: send_sem");
  }

  // critical section: write to shared memeory
  sprintf(send_shared_mem_ptr->buf, "%s", msg);

  // signal availability of message in shared memory
  if (sem_post(send_sem) == -1) {
	this->errormsg("sem_post: send_sem");
  }  

}

// send msg over the shared memory
void shm_sender::send(const myParticleInfo *info) {

  // Wait for shm to become available for writing(the corresponding semaphore is > 0)
  if (sem_wait(sem_send_mutex) == -1) {
	this->errormsg("sem_wait: send_sem");
  }
 
// critical section: write to shared memeory
  memcpy(send_shared_mem_ptr->buf, info, sizeof(struct myParticleInfo) );

  // signal availability of message in shared memory
  if (sem_post(send_sem) == -1) {
	this->errormsg("sem_post: send_sem");
  }  

}
