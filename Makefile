# Main Makefile for the Pyro Python Robotics System
# Please edit Makefile.cfg, or run "make config; make"

# Need a guess to get started:
PYTHON_BIN=python2.2

include Makefile.cfg

# Failing subdir: robot/driver/testc

SUBDIRS = vision/cvision camera/fake camera/blob $(CONFIGDIRS) 

ifeq ($(SAPHIRA),)
else
SUBDIRS += lib robot/driver/saphira 
endif

everything: system/version.py all bin/pyro plugins/simulators/Khepera compile 

include Makefile.src

.PHONY: all tar pyro-$(PYRO_VERSION).tgz cleanall compile

tar: pyro-$(PYRO_VERSION).tgz

config: 
	$(PYTHON_BIN) configure.py
	make

compile:
	$(PYTHON_BIN) compile.py

pyro-$(PYRO_VERSION).tgz: Makefile
	mkdir tars || true
	mv *.tgz tars/ || true
	make cleanall; cd ..; tar cfz pyro-$(PYRO_VERSION).tgz pyro --exclude pyro/plugins/simulators/Khepera --exclude CVS --exclude tars --exclude test --exclude examples --exclude som2 --exclude htmlsom --exclude experiments --exclude data --exclude kRobotClass --exclude simulator --exclude SIM --exclude stuff --exclude misc --exclude Makefile.cfg; mv pyro-$(PYRO_VERSION).tgz pyro; cd -; mv *.tgz tars

Makefile.cfg:
	$(PYTHON_BIN) configure.py

system/version.py: Makefile.src
	echo -e "# This file is automatically generated\ndef version():\n\treturn \"$(PYRO_VERSION)\"" > system/version.py

bin/pyro: Makefile.src build/pyro Makefile.cfg
	echo -e "#!$(PYTHON_BIN)" > bin/pyro
	cat build/pyro >> bin/pyro
	chmod a+x bin/pyro

plugins/simulators/Khepera: build/Khepera Makefile Makefile.cfg Makefile.src
	echo -e "#!/bin/sh" > plugins/simulators/Khepera
	echo -e "SIM_DIR=$(PWD)/simulators/khepera" >> plugins/simulators/Khepera
	cat build/Khepera >> plugins/simulators/Khepera
	chmod a+x plugins/simulators/Khepera

clean:: 
	- $(RM) plugins/simulators/Khepera
	- $(RM) bin/pyro

cleanall:: clean

