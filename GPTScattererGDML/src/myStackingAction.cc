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

#include "myStackingAction.hh"
#include "G4TrackingManager.hh"
#include "G4RunManager.hh"
#include "G4Track.hh"
#include "G4ios.hh"
#include "G4UnitsTable.hh"
#include "G4TrackStatus.hh"
#include "G4ParticleDefinition.hh"
#include "G4ParticleTypes.hh"
#include "G4ios.hh"

myStackingAction::myStackingAction()
{ 
}

myStackingAction::~myStackingAction()
{
}

G4ClassificationOfNewTrack 
myStackingAction::ClassifyNewTrack(const G4Track * aTrack)
{
  G4String name = aTrack->GetDefinition()->GetParticleName();

  // Skip neutrinos
  if ( name == "anti_nu_e" || name == "nu_e") {
    return fKill;
  }
  else {
    return fWaiting;
  }

  
}

void myStackingAction::NewStage()
{
  return;
}
    
void myStackingAction::PrepareNewEvent()
{
  return;
}
