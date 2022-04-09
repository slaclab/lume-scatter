# $Id: GNUmakefile,v 1.3 2005/07/19 08:49:15 flei Exp $
# --------------------------------------------------------------
# GNUmakefile for examples module
# --------------------------------------------------------------
#
# To set geant variables execute
# source /home/hindi/geant/geant4.10.07.p02-build/geant4make.sh
# in current bash shell before running gmake
#
name := GPTScattererGDML
G4TARGET := $(name)
G4EXLIB := true
G4TMP := ./



ifndef G4INSTALL
  G4INSTALL = ../../geant4
endif

.PHONY: all
all: lib bin

#CPPFLAGS += -g -DDEBUG=1
CPPFLAGS += -O2
EXTRALIBS += -lrt -lpthread


include $(G4INSTALL)/config/architecture.gmk
include $(G4INSTALL)/config/binmake.gmk

visclean:
	rm -f g4*.prim g4*.eps g4*.wrl
	rm -f .DAWN_*
