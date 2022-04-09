#ifndef shm_structs_h
#define shm_structs_h 1

struct threeVector {
  double x;
  double y;
  double z;
};

struct myParticleInfo {
  double energy; // energy in keV
  threeVector pos; // position in mm
  threeVector dir; // direction cosines (unitless)
};


#endif
