# March 1998
#
# Makefile for PTZ Camera object
#

SHELL = /bin/sh

#############################################################

SRCD = ./
OBJD = ./
INCD = $(SAPHIRA)/handler/include/
LIBD = $(SAPHIRA)/handler/obj/
BIND = ./
COLBERT = $(SAPHIRA)/colbert/
OAALIB = $(SAPHIRA)/oaa/agents/lib/
SHARED = -shared

# find out which OS we have 
include $(SAPHIRA)/handler/include/os.h

CFLAGS =  -g -D$(CONFIG)
CC = gcc
INCLUDE = -I$(INCD) -I$(X11D)include


#############################################################
all: $(COLBERT)ptzsys.so
	touch all

#
# PTZ camera loadable object file
#

$(OBJD)ptzsys.o: $(SRCD)ptzsys.c $(INCD)saphira.h
	$(CC) $(CFLAGS) -c $(SRCD)ptzsys.c $(INCLUDE) -o $(OBJD)ptzsys.o

$(COLBERT)ptzsys.so: $(OBJD)ptzsys.o
	$(LD) $(SHARED) $(OBJD)ptzsys.o -o libptzsys.so
