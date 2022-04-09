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

#include "myTrackingAction.hh"
#include "G4TrackingManager.hh"
#include "G4RunManager.hh"
#include "G4Track.hh"
#include "G4ios.hh"
#include "G4UnitsTable.hh"
#include <iostream>
#include <string>

myTrackingAction::myTrackingAction()
{
}

void myTrackingAction::PreUserTrackingAction(const G4Track* aTrack)
{
#if 0
  G4String particleName = aTrack->GetDefinition()->GetParticleName();
  if(particleName != "gamma" ) {
    return;
  }

  G4ThreeVector r = aTrack->GetPosition();
  G4ThreeVector p = aTrack->GetVertexMomentumDirection();
  G4ThreeVector v = aTrack->GetVertexPosition();

  G4double energy = aTrack->GetVertexKineticEnergy();
  //  if (energy < 10.0)    return;

  G4RunManager* fRM = G4RunManager::GetRunManager();
  const G4Event *event = fRM->GetCurrentEvent();
  G4int eventNo = event->GetEventID();

  G4cout.precision(6);
  G4cout << energy/CLHEP::keV << " "
	 << v/cm << " "
	 << G4endl;
#endif
}

void myTrackingAction::PostUserTrackingAction(const G4Track* aTrack)
{
}


