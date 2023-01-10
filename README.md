# lume-scatter
Code to perform scattering calculations between GPT and Geant4

## Overview
GPT is a closed source application for simulating the propagation of
charged particles in a variety of electric and magnetic field lensing
systems, including acceleration by electromagnetic waves. It currently
provides a builtin language for describing the beam-line geometry as
2D surfaces. It provides a simple scattering model for a particle that
crosses the beam-line boundary. However, it also allows for linking in
a user-supplied routine to handle the scattering. The code provided
here implements a routine that passes the particle to a running Geant4
application to handle the scattering. The incident particle is passed
to the Geant4 process via POSIX shared memory; the Geant4 process
propagates the particle through a 3D model of the geometry and returns
the scattered particle, or a flag that it has been absorbed, through
shared memory. Coordination between the GPT and Geant4 processes is
handled by semaphores. Python scripts are also provided to convert
the GPT 2D geometry to a 3D GDML model for reading by the Geant4
process, and for viewing the GPT tracks in FreeCAD.

## Prerequisites
- A licensed installation of [GPT](http://www.pulsar.nl).
- A [Geant4](https://geant4.web.cern.ch/) installation. Geant4
  is open-source and freely available.
- Optional (but highly recommended)
  [FreeCAD](https://www.freecadweb.org/), an open source CAD
  application for viewing the 3D geometry and the GPT tracks. The GDML
  add-on Workbench (installable via the FreeCAD Add-on manager), is
  required for viewing the 3D GDML geometry in FreeCAD.
  
The code here has been developed and tested on a Fedora 35 Linux
workstation. It will almost definitely **not** work in Windows; it may
be made to work on a Mac.

## What is provided
- In gpt_elems, the files needed to link GPT with our Geant4-based scatterer
- In GPTScatterer, the Geant4-based application source code
- In gdmlUtils:
  - `gptgeom2gdml.py`: a python script that reads the GPT .in file and
    produces a gdml 3D geometry file
  - `insert_tracks.py` and `tracks_viewer.ui`: files needed to view tracks under FreeCAD
- Samples: sample input/output files (TODO)
- Images: screen shots, etc, (TODO)

## Linking the geant4scaterrer with GPT
1. Copy the files in the gpt_elems directory to the elems directory of your GPT installation:
GPT_INSTALLATION_DIR/GPT344-BEM-Linux/gpt344BEM-CentOS7-devtoolset8-13-oct2021-avx2/elems
2. `cd` to above directory
3. type `make`

This will create a `gpt` executable linked to the geant4scatterer.

## Compiling the Geant4 application
1. [Geant4](https://geant4.web.cern.ch/) must be already installed on
   your system.
2. Make sure the needed environmental variables are set by issuing:
`source PATH_TO_GEANT/geant4.10.07.p02-build/geant4make.sh`
3. `cd` to the GPTScattererGDML directory and
4. type` make`, or `gmake`

## Running a GPT simulation with geant4 as the scaterrer
The following statement has to be in the GPT (.in) input file  
`geant4scatter("wcs", "I", "geant4", 0.01, 2);`  

Then elements that should make use of the geant4 scatterer should
refer to geant4, for example  
`scattercone("wcs","I",0.0, 0.36, 0.04,0.361)scatter="geant4" ;`  

GPT does not provide for specifying materials for its geometrical
elements, but a Geant4 application **requires** volumes to have a
material assigned. To assign a material insert a comment like this
before the element:  
`# {'material': 'G4_STAINLESS-STEEL'}`  
Note that
this has to be a python dictionary, so observe the braces and colons.
The material will apply to all subsequent solids generated, until
another  
`# {'material':}`  
statement is encountered.

Also, Geant4 requires a thickness to convert the GPT 2D boundary to a
solid. You can assign a thickness to the following solid by inserting
a comment:  
`# {'thickness': '2.0'}`  

- make a gdml file out of the geometry in the GPT input file:  
`gptgeom2gdml.py <gpt_input.in> <gpt_gdml.gdml>`  
(replace terms in angle brackets with your file names)

- copy the resulting gdml file to the directory containing the Geant application,
for example:  
`cp gpt_gdml.gdml PATH_TO_GEANT_APPS/GPTScattererGDML`  

- go to the directory containing the Geant application. For example,
`cd PATH_TO_GEANT_APPS/GPTScattererGDML`
- to view the geometry  
`GPTScaterrerGDML gpt_gdml.gdml 1`  
the 1 flag, does not create a shared memory; it is just to test the display of the geometry.
- to run the Geant4 application waiting for particle from gpt:
  - first make sure there are no left over shared memory structures from a prior run:
  `rm /dev/shm/*`

  - then:
  `GPTScaterrerGDML gpt_gdml.gdml 0`

go back to the gpt application directory and run gpt as usual:  
`gpt -o xxx.gdf xxx.in`

You should see `gpt` list the scattered track positions,
directions and energy.

When the gpt run is done you can analyze the output as usual.

I usually follow this with:  
`gdftrans -o tracks.gdf xxx.gdf time x y z G`  
`gdf2a -o tracks.txt tracks.gdf`  

At present there is no graceful exit from the Geant4 application
(`GPTScaterrerGDML`). Simpliy Control-C from the application
terminal. Make sure the clean up the shared memory files afterwords:  
`rm /dev/shm/*`  


## Displaying the geometry and tracks in FreeCAD

- If the GDML Workbench is not already installed, install it via:  
Tools->Addon Manager  
and install GDML

Note that the [GDML](https://github.com/KeithSloan/GDML) Workbench has
been developed by Keith Sloan, and Munther Hindi is one of the
contributors. We are adding functionalities continually in response to
users' feedback.

- open the gdml file via File->open...

Note on volume naming: Currently gpt does not provide for naming the
scatter elements, so the names `gptgeom2gdml.py` creates for the solids
are appended with the line number in the gpt input file where the
element was declared.

## Exploring the geometry in FreeCAD

Copy the files insert_tracks.py and tracks_viewer.ui to `~/.FreeCAD/Macro/`

Execute the Macro (via Macro->Macros...) in FreeCAD and select
`insert_tracks.py`. A dialog should pop up. Load the tracks file (for
example, the `trakcs.txt` file produced above). This will insert the
tracks in the currently active document. The dialog also allows
hiding/viewing the tracks, and displaying their intersection with a
screen that can be moved along the z-axis. 

If the input file to gpt specifies the number of particles as np0 (say,
100), then the tracks with IDs 1-np0 are the primary tracks generated
by gpt and tracks np0+1-... are those generated by geant. In FreeCAD each
track entity generated by inser_tracks is called tracknnn, where nnn
is the ID of the track. To display the scattered track in a different
color, for example, select tracks track101-end, right click, select
Appearance... and change Line color and Point Color to your taste.

In the dialog, you can enter np0 as the Max primary ID. With id less
than that will be colored differently (currently cyan), than tracks
that come after that (the scattered tracks, currently colored red).

Note that you can save the current geometry (+ tracks) as a standard
FreeCAD file (.FCstd) for later exploring and/or modification.


## Caveats, thoughts on TODOs

1. The GPTScatterScatterer geant application now processes the gpt
  tracks with a run for each track sent by gpt via a `/run/beamOn 1`
  command. This has quite an overhead since geant seems to regenerate
  the cross section tables for all the elements before each run (I am
  not sure it does, but the cuts for each particle in each material
  seem to be reprinted again at the beginning of each run). A speedier
  approach might be to buffer the gpt tracks into shared memeory, and
  then have `myEventGenerator->generateEvent`, scan the shared memory
  and generate an event for each track (instead of the current run for
  each track). The number of events would have to be included in the
  shared memeory. In the (far) future, a version with parallel threads
  (MPI) could be provided.

2. The Geant4 application only returns back to gpt the primary
   particle; if the particle is absorbed it returns 0 for its energy
   as a signal to the scattering routine that it should remove the
   particle. So true secondaries (very low energy electrons) are not
   returned to gpt.

3. TODO: provide a more graceful way to exit and automatically delete
   (and/or reuse) the shared memory files.

