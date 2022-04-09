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
#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4UIGAG.hh"
#include "G4UIterminal.hh"
#include "G4UItcsh.hh"
#include "G4UIExecutive.hh"
#include "G4LogicalVolumeStore.hh"

//#include "G4UIQt.hh"
#ifdef G4UI_USE_XM
#include "G4UIXm.hh"
#endif 

#include "G4EmCalculator.hh"
#include "G4GDMLParser.hh"

#include "PhysicsList.hh"
#include "myEventAction.hh"
#include "Randomize.hh"
#include "simplePrimaryGeneratorAction.hh"
#include "myTrackingAction.hh"
#include "myStackingAction.hh"
#include "myRunAction.hh"
#include "DetectorConstruction.hh"
#include "mySteppingAction.hh"

#include "shm_sender.hh"
#include "shm_receiver.hh"

#ifdef G4VIS_USE
#include "G4VisExecutive.hh"
#endif

void print_aux(const G4GDMLAuxListType* auxInfoList, G4String prepend="|")
{
  for(std::vector<G4GDMLAuxStructType>::const_iterator
      iaux = auxInfoList->begin(); iaux != auxInfoList->end(); iaux++ )
    {
      G4String str=iaux->type;
      G4String val=iaux->value;
      G4String unit=iaux->unit;

      G4cout << prepend << str << " : " << val  << " " << unit << G4endl;

      if (iaux->auxList) print_aux(iaux->auxList, prepend + "|");
    }
  return;
}

void addColor(G4String lvName, G4String color){
  std::stringstream ss;
  unsigned int r, g, b, a;

  std::string rs, gs, bs, as;
  rs = "0x"+color.substr(1,2);
  gs = "0x"+color.substr(3,2);
  bs = "0x"+color.substr(5,2);
  sscanf(rs.c_str(), "%x", &r);
  sscanf(gs.c_str(), "%x", &g);
  sscanf(bs.c_str(), "%x", &b);
  
  a = 256;
  if(color.length() == 9) { // includes the #
	as = "0x"+color.substr(7,2);
	sscanf(as.c_str(), "%x", &a);
  }

  G4UImanager* UImanager = G4UImanager::GetUIpointer();
  char cmd[1024];
  sprintf(cmd, "/vis/geometry/set/colour %s %f %f %f %f",
		  lvName.c_str(), r/256., g/256., b/256., 1.0 - a/256.);
  G4cout << cmd << G4endl;
  UImanager->ApplyCommand(cmd);
  
}

int main(int argc, char** argv)
{
   G4cout << G4endl;
   G4cout << "Usage:" << argv[0] << "  <intput_gdml_file> "
		  << "<interactive: [1|0] >"
		  << G4endl;
   G4cout << G4endl;

   if (argc != 3)
   {
      G4cout << "Two arguments needed " << G4endl;
      G4cout << G4endl;
      return -1;
   }

#ifdef G4VIS_USE
  // visualization manager
  G4VisManager* visManager = new G4VisExecutive;
  visManager->Initialize();
#endif

   G4GDMLParser parser;

   parser.SetOverlapCheck(true);
   parser.Read(argv[1]);

   ///////////////////////////////////////////////////////////////////////
   //
   // Example how to retrieve Auxiliary Information
   //

   G4cout << std::endl;

   const G4LogicalVolumeStore* lvs = G4LogicalVolumeStore::GetInstance();
   std::vector<G4LogicalVolume*>::const_iterator lvciter;
   for( lvciter = lvs->begin(); lvciter != lvs->end(); lvciter++ )
   {
     G4GDMLAuxListType auxInfo = parser.GetVolumeAuxiliaryInformation(*lvciter);

     if (auxInfo.size()>0) {
       G4cout << "Auxiliary Information is found for Logical Volume :  "
              << (*lvciter)->GetName() << G4endl;
	   for(std::vector<G4GDMLAuxStructType>::const_iterator
			 iaux = auxInfo.begin(); iaux != auxInfo.end(); iaux++ )
		 {
		   G4String str=iaux->type;
		   G4String val=iaux->value;
		   G4String unit=iaux->unit;

		   if(str == "Color") {
			 addColor((*lvciter)->GetName(), val);
		   }
		 }
	 }

     print_aux(&auxInfo);
   }


   bool interactive = strcmp(argv[2], "0") != 0;


  // random engine
  CLHEP::HepRandom::setTheEngine(new CLHEP::RanecuEngine);
  for (int i=0; i < 20; i++) {
	G4cout << RandFlat::shoot(0.0,1.0) << G4endl;
  }

  // Construct the default run manager
  G4RunManager* runManager = new G4RunManager;

  // set mandatory initialization classes

  DetectorConstruction* Detector = new DetectorConstruction(parser.GetWorldVolume());
  runManager->SetUserInitialization(Detector);
  runManager->SetUserInitialization(new PhysicsList);

  // set mandatory user action class
  runManager->SetUserAction(new SimplePrimaryGeneratorAction);
  runManager->SetUserAction(new myRunAction);
  //runManager->SetUserAction(new ExTGRunAction);
  runManager->SetUserAction(new myEventAction);
  runManager->SetUserAction(new myStackingAction);
  runManager->SetUserAction(new myTrackingAction);

  if(!interactive) {
	shm_sender *track_output_sender = new shm_sender("/sem-resp-mutex", "/sem-resp", "/backscattered_particle");
	runManager->SetUserAction(new mySteppingAction(track_output_sender));
  }
  else {
	runManager->SetUserAction(new mySteppingAction(0));
  }
  //
  //
 

  // get the pointer to the User Interface manager 
  G4UIExecutive* ui = 0;
  ui = new G4UIExecutive(argc, argv);
  G4String command = "/control/execute initInter.mac";
  G4UImanager* UI = G4UImanager::GetUIpointer();  
  UI->ApplyCommand(command);

  if(interactive) {
	ui->SessionStart();
	delete ui;
  }
  else {
	shm_receiver *shm_recv = new shm_receiver("/sem-send-mutex", "/sem-send", "/incident_particle");
	shm_recv->start();
  }
  
  // job termination
#ifdef G4VIS_USE
  delete visManager;
#endif
  //  delete analysis;
  delete runManager;

  return 0;
}








