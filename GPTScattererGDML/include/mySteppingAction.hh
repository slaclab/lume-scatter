//
// ********************************************************************
// * DISCLAIMER                                                       *
// *                                                                  *
// * The following disclaimer summarizes all the specific disclaimers *
// * of contributors to this software. The specific disclaimers,which *
// * govern, are listed with their locations in:                      *
// *   http://cern.ch/geant4/license                                  *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.                                                             *
// *                                                                  *
// * This  code  implementation is the  intellectual property  of the *
// * GEANT4 collaboration.                                            *
// * By copying,  distributing  or modifying the Program (or any work *
// * based  on  the Program)  you indicate  your  acceptance of  this *
// * statement, and all its terms.                                    *
// ********************************************************************
//
//
// $Id: mySteppingAction.hh,v 1.1.1.1 2009/04/22 18:54:54 hindi Exp $
// GEANT4 tag $Name: start_1_0_0 $
// 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....

#ifndef mySteppingAction_h
#define mySteppingAction_h 1

#include "G4UserSteppingAction.hh"
#include "shm_sender.hh"
#include "shm_structs.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....

class mySteppingAction : public G4UserSteppingAction
{
public:
  mySteppingAction(shm_sender *shm);
  ~mySteppingAction(){};
  
  void UserSteppingAction(const G4Step*);
  
private:
  shm_sender *shm_track_sender;
  char buf[256];
  myParticleInfo myScatteredParticle;
  
};

#endif
