# Main Makefile for the Pyrobot Python Robotics System
# Please edit Makefile.cfg, or run "make config; make"

# Need a guess to get started:
PYTHON_BIN=python

include Makefile.cfg

# Failing subdir: robot/driver/testc

SUBDIRS =  $(CONFIGDIRS) 

everything: system/version.py all plugins/simulators/KheperaSimulator compile \
	bin/pyrobot

include Makefile.src

.PHONY: all tar pyrobot-$(PYROBOT_VERSION).tgz clean compile

tar: pyrobot-$(PYROBOT_VERSION).tgz

config: system/version.py
	$(PYTHON_BIN) configure.py
	make

compile:
	$(PYTHON_BIN) compile.py

pyrobot-$(PYROBOT_VERSION).tgz: Makefile
	mkdir download || true
	mv *.tgz download/ || true
	make clean; cd ..; tar cfz pyrobot-$(PYROBOT_VERSION).tgz pyrobot --exclude fedora --exclude stylesheet.css --exclude knoppix --exclude CVS --exclude tars --exclude download --exclude Makefile.cfg; mv pyrobot-$(PYROBOT_VERSION).tgz pyrobot; cd -; mv *.tgz download
	$(RM) -f download/pyrobot-latest.tgz
	cd download; ln -s pyrobot-$(PYROBOT_VERSION).tgz pyrobot-latest.tgz

Makefile.cfg:
	$(PYTHON_BIN) configure.py

system/version.py: Makefile.src
	echo -e "# This file is automatically generated\ndef version():\n\treturn \"$(PYROBOT_VERSION)\"" > system/version.py

bin/pyrobot: Makefile.cfg Makefile Makefile.src build/pyrobot system/version.py
	echo -e "#!$(PYTHON_BIN)" > bin/pyrobot
	cat build/pyrobot >> bin/pyrobot
	chmod a+x bin/pyrobot

plugins/simulators/KheperaSimulator: build/Khepera Makefile Makefile.cfg Makefile.src
	echo -e "#!/bin/sh" > plugins/simulators/KheperaSimulator
	echo -e "SIM_DIR=$(PWD)/simulators/khepera" >> plugins/simulators/KheperaSimulator
	cat build/Khepera >> plugins/simulators/KheperaSimulator
	chmod a+x plugins/simulators/KheperaSimulator

clean:: 
	- $(RM) plugins/simulators/KheperaSimulator
	- $(RM) system/version.py
	- $(RM) bin/pyrobot

