/*
 *
 *      client for a Geant4 server. Read user input, assumed an energy and a theta (NO VALIDATION)
 *      send to shared memory. raise semaphore to trigger geant to read the shm. Wait for read semaphore
 *      to read response from another shared memory buffer. Anser is energy, theta and phi of backscattered
 *      electron. Energy = 0 indicates no backscatter. Note in this version we expected one backscattered
 *      event per incident particle.
 *                 
 */

#include "bidirectional_shm_client.hh"

// buffer zero for writing into from this process, buffer 1 to read back results
#define MAX_BUFFERS 2

#define LOGFILE "/tmp/example.log"

/*
 * Bidirectional communication and semaphore logic:
 * There are two shared memory areas, one for sending data (shm_send) and one for receiving
 * response (shm_resp). Access to the sahred memory is syncronized by two semaphores, for each
 * memory. One semaphore is two guarantee mutual exclusion for access to the shared memory (a mutex semaphore)
 * and the other is signal availability of data to read from the memeory.
 * The pseudo code for communication is as follows:
 *
 * sending process:
 * prepare/fetch message
 * sem_wait(sem_mutex) // wait for exclusive access to memory
 * write message to shared memeory
 * sem_post(sem_send)  //signal to receiving process that there is something to read
 *
 * receiving process:
 * sem_post(sem_mutex) // initialize mutex for shm to be available
 * while(1) { //continuously wait for messages
 *   sem_wait(sem_send) // wait for a signal that there is a message
 *   read message from shared memory
 *   sem_post(sem_mutex) // release mutex for shared memory
 * }
 */

#define SEM_RESP_MUTEX_NAME "/sem-resp-mutex"
#define SEM_SEND_MUTEX_NAME "/sem-send-mutex"
#define SEM_SEND_NAME "/sem-send"
#define SEM_RESP_NAME "/sem-resp"
#define SEND_SHARED_MEM_NAME "/incident_particle"
#define RESP_SHARED_MEM_NAME "/backscattered_particle"

// Print system error and exit
void bidirectional_shm_client::error(string msg)
{
  perror(msg.c_str());
    exit (1);
}

bidirectional_shm_client::bidirectional_shm_client()
{
    
    // semaphore for mutual exclusion to send buffer
    if ((sem_send_mutex = sem_open(SEM_SEND_MUTEX_NAME, 0, 0, 0)) == SEM_FAILED)
	  error ("sem_send_mutex sem_open");

    // semaphore for mutual exclusion to recv buffer
    if ((sem_resp_mutex = sem_open(SEM_RESP_MUTEX_NAME, 0, 0, 0)) == SEM_FAILED)
        error ("sem_resp_mutex sem_open");

    // semaphore to allow writing into send buffer
    if ((send_sem = sem_open(SEM_SEND_NAME, 0, 0, 0)) == SEM_FAILED)
        error ("send_sem sem_open");

	// semaphore to allow reading from response buffer
    if ((resp_sem = sem_open(SEM_RESP_NAME, 0, 0, 0)) == SEM_FAILED)
        error ("resp_sem sem_open");

    // Get shared memory file descriptors for send, resp buffers
    if ((fd_send_shm = shm_open(SEND_SHARED_MEM_NAME, O_RDWR, 0)) == -1)
        error ("send shm_open");
    if ((fd_resp_shm = shm_open(RESP_SHARED_MEM_NAME, O_RDWR, 0)) == -1)
        error ("resp shm_open");

    if ((send_shared_mem_ptr = (shared_memory *) mmap (NULL, sizeof (struct shared_memory), PROT_READ | PROT_WRITE, MAP_SHARED,
									 fd_send_shm, 0)) == MAP_FAILED)
	  error ("send mmap");
	
	if ((resp_shared_mem_ptr = (shared_memory *) mmap (NULL, sizeof (struct shared_memory), PROT_READ | PROT_WRITE, MAP_SHARED,
									 fd_resp_shm, 0)) == MAP_FAILED)
	  error ("resp mmap");

		//initialize response shared memory to be available for writing into
    if (sem_post(sem_resp_mutex) == -1) {
	  error ("sem_post: sem_resp_mutex");
	}
}

int bidirectional_shm_client::scatterParticle(myParticleInfo *in, myParticleInfo *out)
{
	// wait for send buffer to be available: P (buffer_count_sem);
	// this waits for the send_sem count to become 1 (i,e, the server must set to one after reading,
	// to indicate it is availabe
	if (sem_wait(sem_send_mutex) == -1) {
	  error ("sem_wait: sem_send_mutex");
	}

	/*
	sprintf(send_shared_mem_ptr->buf, "%lf %lf %lf %lf %lf %lf %lf",
			inPos->x, inPos->y, inPos->z,
			inDirection->x, inDirection->y, inDirection->z);
	*/
	memcpy(send_shared_mem_ptr->buf, in, sizeof(struct myParticleInfo));
	
	// Release send_sem: V (send_sem)
	if (sem_post(send_sem) == -1) {
	  error ("sem_post: mutex_sem");
	}
    
	// now wait for response
	if (sem_wait(resp_sem) == -1) {
	  error ("sem_wait: resp_sem");
	}

	memcpy(out, resp_shared_mem_ptr->buf, sizeof(struct myParticleInfo));
	//for debugging
	/*
	fprintf(stdout, "received response: %lf (%lf, %lf, %lf) (%lf, %lf, %lf) \n",
			out->energy,
			out->pos.x, out->pos.y, out->pos.z,
			out->dir.x, out->dir.y, out->dir.z);
	*/
	// Release exclusion on response shm: V (send_sem)
	if (sem_post(sem_resp_mutex) == -1) {
	  error ("sem_post: sem_resp_mutex");
	}

	return 1;
}

bidirectional_shm_client::~bidirectional_shm_client()
{
  if (munmap (send_shared_mem_ptr, sizeof (struct shared_memory)) == -1) {
	error ("munmap");
  }
  if (munmap (resp_shared_mem_ptr, sizeof (struct shared_memory)) == -1) {
	error ("munmap");
  }
}


