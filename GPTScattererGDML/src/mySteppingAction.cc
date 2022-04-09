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
// $Id: mySteppingAction.cc,v 1.1.1.1 2009/04/22 18:54:54 hindi Exp $
// GEANT4 tag $Name: start_1_0_0 $
// 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....

#include "mySteppingAction.hh"
#include "G4SteppingManager.hh"
#include "G4EventManager.hh"
#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4VPhysicalVolume.hh"

extern "C" {
#include <stdio.h>
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....

mySteppingAction::mySteppingAction(shm_sender *sender)
  : shm_track_sender(sender)
{ }

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....

void mySteppingAction::UserSteppingAction(const G4Step* aStep)
{   
  G4Track *track = aStep->GetTrack();
  //only process the primary track
  if(track->GetParentID() != 0 ) { // for now only backscatter the primary electron
	//G4cout << "not primary beam" << G4endl;
	return; 
  }

  G4double energy = track->GetKineticEnergy()/CLHEP::keV;
  if (energy < 0.4) { // last step not in World, signal a track stopping in the material
	G4cout << "Energy less than 0.4 keV" << G4endl;
	G4cout << "0 0 0 0 0 0 0" << G4endl;
	if(shm_track_sender) {
	  myScatteredParticle.energy = 0;
	  shm_track_sender->send(&myScatteredParticle);
	}
	track->SetTrackStatus(fStopAndKill);
	return;
  }

  // skip if the step starts in the World volume
  G4StepPoint *preStepPoint = aStep->GetPreStepPoint();
  G4VPhysicalVolume *phys0 =  preStepPoint->GetPhysicalVolume();
  G4StepPoint *postStepPoint = aStep->GetPostStepPoint();
  G4VPhysicalVolume *phys1 =  postStepPoint->GetPhysicalVolume();

#ifdef DEBUG
  // Debugging the step
	if(phys0) {
	  G4cout << "pre: " << phys0->GetName() << " status " << preStepPoint->GetStepStatus() << G4endl;
	  G4ThreeVector r = preStepPoint->GetPosition();
	  G4ThreeVector p = track->GetMomentumDirection();
	  r /= CLHEP::mm;
	  
	  G4cout.precision(4);
	  G4cout << energy << "\t"
			 << r << "\t"
			 << p << "\t"	
			 << G4endl;
	}
	if(phys1) {
	  G4cout << "post: " << phys1->GetName() << " status " << postStepPoint->GetStepStatus() << G4endl;
	  G4ThreeVector r = postStepPoint->GetPosition();
	  G4ThreeVector p = track->GetMomentumDirection();
	  r /= CLHEP::mm;
	  
	  G4cout.precision(4);
	  G4cout << energy << "\t"
			 << r << "\t"
			 << p << "\t"	
			 << G4endl;
	}

  if(phys1 == 0) {
	G4cout << "post volume is null" << G4endl;
  }
#endif

  if(phys1 == 0) {
	G4cout << "poststep OutOfWorld" << G4endl;
	G4cout << "0 0 0 0 0 0 0" << G4endl;
	if(shm_track_sender) {
	  myScatteredParticle.energy = 0;
	  shm_track_sender->send(&myScatteredParticle);
	}
	return;
  }

  if(phys0 != 0 && phys0->GetName() == "World_PV") {
	G4cout << "prestep in World" << G4endl;
	return;
  }
  
  //G4String name = track->GetDefinition()->GetParticleName();

  // Skip anything not an electron
  /*
  if ( name != "e-" && name != "geantino") { // geantino used for testing
    return;
  }
  */

  if(postStepPoint->GetStepStatus() == fGeomBoundary ) {
	// We keep going until we either stop, or get back to the world volume.
	// i.e., we DON'T stop of we cross a boundary to another material (not the World)
	if (phys1->GetName() != "World_PV" ) {
#ifdef DEBUG
	  G4cout << "boundary not in World" << G4endl;
#endif
	  return;
	}
	
	G4ThreeVector r = postStepPoint->GetPosition();
	G4ThreeVector p = track->GetMomentumDirection();
	G4ThreeVector v = track->GetVertexPosition();
	r /= CLHEP::mm;
	
	// if (energy < 1.0)    return; will let receiving/analyzing program deal with energy cut
	
	/*
	  G4RunManager* fRM = G4RunManager::GetRunManager();
	  const G4Event *event = fRM->GetCurrentEvent();
	  G4int eventNo = event->GetEventID();
	*/
	
	G4cout.precision(4);
	G4cout << energy << "\t"
		   << r << "\t"
		   << p << "\t"	
		   << G4endl;
	
	
	if(shm_track_sender) {
	  myScatteredParticle.energy = energy;
	  myScatteredParticle.pos.x = r.x();
	  myScatteredParticle.pos.y = r.y();
	  myScatteredParticle.pos.z = r.z();
	  myScatteredParticle.dir.x = p.x();
	  myScatteredParticle.dir.y = p.y();
	  myScatteredParticle.dir.z = p.z();
	  
	  //	  std::sprintf(buf, "%lf %lf %lf %lf %lf %lf %lf", energy, r.x(), r.y(), r.z(), p.x(), p.y(), p.z());
	  // shm_track_sender->send(buf);
	  shm_track_sender->send(&myScatteredParticle);
	}	
	track->SetTrackStatus(fStopAndKill);
	return;
  }
  /*
  else if (energy < 1.0) { // last step not in World, signal a track stopping in the material
	G4cout << "0 0 0 0 0 0 0" << G4endl;
	if(shm_track_sender) {
	  myScatteredParticle.energy = 0;
	  shm_track_sender->send(&myScatteredParticle);
	}
	track->SetTrackStatus(fStopAndKill);
  }
  */

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....
