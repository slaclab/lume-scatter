# UNIX Makefile for ELEMS

include ../makeinc.gcc

TARGETS = gpt$(EXEEXT)
all: $(TARGETS)

include makefile.ele
ELEMOBJSO = $(ELEMOBJS:.obj=.o) bidirectional_shm_client.o

CFLAGS += -g -I../kernel -I.
LDFLAGS += -lrt -lpthread
CC = $(MPICC)

#elemlist:
#	echo "# List your custom GPT-elements in two columns: name filename (where the filename must be listed WITHOUT .c extension)" > elemlist

bidirectional_shm_client.o: bidirectional_shm_client.cc bidirectional_shm_client.hh 	shm_structs.hh
		$(CC) $(CFLAGS) -c bidirectional_shm_client.cc -o bidirectional_shm_client.o 

elemlist: geant4scatter.c

gps.c: elemlist
	../bin/makeelems ../kernel/elemkrnl elemlist
	@echo Please rerun make.

gpt: gps.o $(ELEMOBJSO) ../kernel/elems.a ../kernel/gps.a ../kernel/gdf.a ../kernel/utils.a
	$(CC) $(LDFLAGS) $(TARGET_ARCH) -o $@ gps.o $(ELEMOBJSO) ../kernel/elems.a ../kernel/gps.a ../kernel/gdf.a ../kernel/utils.a
	$(CP) gpt ../bin

clean:
	$(RM) gpt $(ELEMOBJSO) gps.c
