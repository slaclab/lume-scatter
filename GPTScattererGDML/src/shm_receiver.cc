#include "shm_receiver.hh"

#include "G4ios.hh"
#include "G4UnitsTable.hh"
#include "CLHEP/Units/SystemOfUnits.h"
#include <string>
#include "G4UImanager.hh"

// Print system error and exit
void shm_receiver::errormsg (std::string msg) {
  perror (msg.c_str());
  exit (1);
}


shm_receiver::shm_receiver(string mutex_sem_name, string sem_name, string shm_name)
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

  if ((shared_mem_ptr = (shared_memory *) mmap(NULL, sizeof (struct shared_memory), PROT_READ | PROT_WRITE, MAP_SHARED,
								   fd_send_shm, 0)) == MAP_FAILED)
	this->errormsg("send mmap");
}

shm_receiver::~shm_receiver() {
  if (munmap (shared_mem_ptr, sizeof (struct shared_memory)) == -1) {
	errormsg("munmap");
  }
}

// receive messages over the shared memory
void shm_receiver::start() {

  char mybuf [256];

  G4UImanager* UI = G4UImanager::GetUIpointer();
  // Initialization complete; now we can set mutex semaphore as 1 to 
  // indicate shared memory segment is available
  if (sem_post(sem_send_mutex) == -1)
	this->errormsg ("sem_post: sem_send_mutex");

  myParticleInfo in;
  
  while(1) {
	// Wait for shm to become available (the corresponding semaphore is > 0)
	if (sem_wait(send_sem) == -1) {
	  this->errormsg("sem_wait: send_sem");
	}
	
	// critical section: write to shared memeory
	memcpy(&in, shared_mem_ptr->buf, sizeof(struct myParticleInfo) );
  
	// remove mutex from shared memory
	if (sem_post(sem_send_mutex) == -1) {
	  this->errormsg("sem_post: send_sem");
	}

	int n  = sprintf(mybuf, "/gun/energy %lf keV", in.energy);

	UI->ApplyCommand(mybuf);

	n  = sprintf(mybuf, "/gun/position %lf %lf %lf mm", in.pos.x, in.pos.y, in.pos.z);
	UI->ApplyCommand(mybuf);

	n  = sprintf(mybuf, "/gun/direction %f %f %f", in.dir.x, in.dir.y, in.dir.z);
	G4cout << mybuf << G4endl;
	

	UI->ApplyCommand("/run/beamOn 1");
	
  }

}
