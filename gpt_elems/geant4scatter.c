#define _GLIBCXX_USE_CXX11_ABI 0

#include <stdio.h>
#include <math.h>
#include "elem.h"

#include "bidirectional_shm_client.hh"

#include <string>

#define EXTRAPOLATE 1e-6

#define me 510.998950; //electron mass in keV
void geant4scatter_scat(gptpar *par, double t, double dt, gpttrajectory *trajectory, void *inf);

struct geant4_info {
  bidirectional_shm_client *shm_client;
  struct scatter_info scatinfo;
};

static gptparset *scatteredParticleSet;

void testFunc(const std::string &name) {
  printf("%s\n", name.c_str());
}

void geant4scatter_init(gptinit *init) {
  gptbuildECS(init);
  
  if( gptgetargnum(init) != 3) {
	gpterror("Syntax: %s(ECS, name, p0, p1); \n", gptgetname(init));
  }

  const char *name = gptgetargstring(init, 1);
  printf("Message: %s\n", name);

  struct geant4_info *info;
  info = (geant4_info *) gptmalloc(sizeof(struct geant4_info));
  gptscatterinit(init, &info->scatinfo, name);
  gptinstallscatterfnc(name, geant4scatter_scat, info);

  std::string const setname = "geantScattered";
  scatteredParticleSet = gptcreateparset(gptgetargstring(init, 1));

  bidirectional_shm_client *shm_client = new bidirectional_shm_client();
  info->shm_client = shm_client; 
 
}

void geant4scatter_scat(gptpar *par, double t, double dt,
						gpttrajectory *traj, void *info)
{

  myParticleInfo inPart, outPart;
  
  gptscatterinitpar(&((struct geant4_info *)info)->scatinfo);
  double G = traj->Gint;
  double K = (G-1)*me;
  double GB;

  double r[3];
  double GBr[3];
  int len; // number of particles in scattered set
  
  inPart.energy = K;

  inPart.pos.x = traj->P[0]*1000;
  inPart.pos.y = traj->P[1]*1000;
  inPart.pos.z = traj->P[2]*1000;
  
  inPart.dir.x = traj->ndr[0];
  inPart.dir.y = traj->ndr[1];
  inPart.dir.z = traj->ndr[2];

  
  ((struct geant4_info *) info)->shm_client->scatterParticle(&inPart, &outPart);
  if (outPart.energy == 0) { // remove particle
	gptscatterremoveparticle(&((struct geant4_info *)info)->scatinfo,
							 traj, par);
  }
  else { // add a scattered particle to the scattered set
	// const std::string name = "scattered";
	// gptparset *set = gptgetparset(name);
	//testFunc("this is a test");
	
	r[0] = outPart.pos.x/1000;
	r[1] = outPart.pos.y/1000;
	r[2] = outPart.pos.z/1000;
	//move particle away from surface
	r[0] += outPart.dir.x*EXTRAPOLATE;
	r[1] += outPart.dir.y*EXTRAPOLATE;
	r[2] += outPart.dir.z*EXTRAPOLATE;

	G = 1 + outPart.energy/me;
	GB = sqrt(G*G -1 );
	GBr[0] = GB*outPart.dir.x;
	GBr[1] = GB*outPart.dir.y;
	GBr[2] = GB*outPart.dir.z;

	
	gptscatteraddparmqnartid(&((struct geant4_info *) info)->scatinfo,
							 scatteredParticleSet, r, GBr,
							 par->m, par->q, par->n, par->axis,
							 sqrt(par->r2), t+dt);
	
	gptscatterremoveparticle(&((struct geant4_info *)info)->scatinfo,
							 traj, par);

	printf("ID %d: t: %g, dt %g, tstart %g, pos (%.3f,%.3f,%.3f) dir(%.3f,%.3f,%.3f) K=%.6f\n",
		   par->ID, t, dt, par->tstart,
		   r[0], r[1], r[2],
		   outPart.dir.x, outPart.dir.y, outPart.dir.z, outPart.energy);
	
	  
  }
  
  /*
  
  printf("ID %d: t: %g, dt %g, pos (%.3f,%.3f,%.3f) direction(%.3f,%.3f,%.3f) K=%.6f\n",
		 par->ID, t, dt,
		 traj->P[0]*1000, traj->P[1]*1000, traj->P[2]*1000,
		 traj->ndr[0], traj->ndr[1], traj->ndr[2], K);
  */
  
}
