# Main Makefile for the Pyro Python Robotics System
# Please edit Makefile.cfg

include Makefile.cfg

SUBDIRS = camera/bt848 geometry gui/3DArray robot/driver/grid \
	robot/driver/video camera/v4l brain/psom tools/cluster \
	brain/psom/csom_src/som_pak-dev simulators/khepera

# Failing subdir: robot/driver/testc

ifeq ($(SAPHIRA),)
else
SUBDIRS += lib robot/driver/saphira 
endif

everything: system/version.py all bin/pyro plugins/simulators/Khepera

include Makefile.src

.PHONY: all tar pyro-$(PYRO_VERSION).tgz cleanall

tar: pyro-$(PYRO_VERSION).tgz

config: 
	python configure.py
	make

pyro-$(PYRO_VERSION).tgz: Makefile
	mkdir tars || true
	mv *.tgz tars/ || true
	make cleanall; cd ..; tar cfz pyro-$(PYRO_VERSION).tgz pyro --exclude CVS --exclude tars --exclude test --exclude examples --exclude som2 --exclude htmlsom --exclude experiments --exclude data --exclude kRobotClass --exclude simulator --exclude SIM --exclude stuff --exclude misc; mv pyro-$(PYRO_VERSION).tgz pyro; cd -; mv *.tgz tars

Makefile.cfg:
	python configure.py

system/version.py: Makefile.src
	echo -e "# This file is automatically generated\ndef version():\n\treturn \"$(PYRO_VERSION)\"" > system/version.py

bin/pyro: Makefile.src build/pyro Makefile.cfg
	echo -e "#!/usr/bin/env python$(PYTHON_VERSION)" > bin/pyro
	cat build/pyro >> bin/pyro
	chmod a+x bin/pyro

plugins/simulators/Khepera: build/Khepera Makefile
	echo -e "#!/bin/sh" > plugins/simulators/Khepera
	echo -e "SIM_DIR=$(PWD)/simulators/khepera" >> plugins/simulators/Khepera
	cat build/Khepera >> plugins/simulators/Khepera
	chmod a+x plugins/simulators/Khepera

cleanall::
	$(RM) Makefile.cfg
	rm -rf `find . | grep \.pyc$$`
	rm -rf `find . | grep ~$$`
