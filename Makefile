# Main Makefile for the Pyro Python Robotics System
# Please edit Makefile.cfg, or run "make config; make"

# Need a guess to get started:
PYTHON_BIN=python

include Makefile.cfg

# Failing subdir: robot/driver/testc

SUBDIRS =  $(CONFIGDIRS) 

everything: system/version.py all bin/pyro plugins/simulators/KheperaSimulator compile 

include Makefile.src

.PHONY: all tar pyro-$(PYRO_VERSION).tgz clean compile

tar: pyro-$(PYRO_VERSION).tgz

config: 
	$(PYTHON_BIN) configure.py
	make

compile:
	$(PYTHON_BIN) compile.py

pyro-$(PYRO_VERSION).tgz: Makefile
	mkdir tars || true
	mv *.tgz tars/ || true
	make clean; cd ..; tar cfz pyro-$(PYRO_VERSION).tgz pyro --exclude wikiparser.php --exclude stylesheet.css --exclude knoppix --exclude pyro/plugins/simulators/KheperaSimulator --exclude CVS --exclude tars --exclude test --exclude examples --exclude som2 --exclude htmlsom --exclude experiments --exclude data --exclude kRobotClass --exclude simulator --exclude SIM --exclude stuff --exclude misc --exclude Makefile.cfg; mv pyro-$(PYRO_VERSION).tgz pyro; cd -; mv *.tgz tars
	rm tars/pyro-latest.tgz
	ln -s pyro-$(PYRO_VERSION).tgz 

Makefile.cfg:
	$(PYTHON_BIN) configure.py

system/version.py: Makefile.src
	echo -e "# This file is automatically generated\ndef version():\n\treturn \"$(PYRO_VERSION)\"" > system/version.py

bin/pyro: Makefile.src build/pyro Makefile.cfg
	echo -e "#!$(PYTHON_BIN)" > bin/pyro
	cat build/pyro >> bin/pyro
	chmod a+x bin/pyro

plugins/simulators/KheperaSimulator: build/Khepera Makefile Makefile.cfg Makefile.src
	echo -e "#!/bin/sh" > plugins/simulators/KheperaSimulator
	echo -e "SIM_DIR=$(PWD)/simulators/khepera" >> plugins/simulators/KheperaSimulator
	cat build/Khepera >> plugins/simulators/KheperaSimulator
	chmod a+x plugins/simulators/KheperaSimulator

clean:: 
	- $(RM) plugins/simulators/KheperaSimulator
	- $(RM) bin/pyro
	- $(RM) system/version.py

