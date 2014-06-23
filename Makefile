# Main Makefile for the Pyrobot Python Robotics System
# Please edit Makefile.cfg, or run "make config; make"

# Need a guess to get started:
PYTHON_BIN=python

include Makefile.cfg

# Failing subdir: robot/driver/testc

SUBDIRS =  $(CONFIGDIRS) 

everything: all compile bin/pyrobot

include Makefile.src

.PHONY: all tar pyrobot-$(PYROBOT_VERSION).tgz clean compile

tar: pyrobot-$(PYROBOT_VERSION).tgz

config: Makefile.src
	$(PYTHON_BIN) configure.py
	make

compile:
	$(PYTHON_BIN) compile.py

pyrobot-$(PYROBOT_VERSION).tgz: Makefile
	mkdir download || true
	mv *.tgz download/ || true
	make clean; cd ..; tar cfz pyrobot-$(PYROBOT_VERSION).tgz --exclude fedora --exclude stylesheet.css --exclude knoppix --exclude CVS --exclude tars --exclude download --exclude Makefile.cfg pyrobot; mv pyrobot-$(PYROBOT_VERSION).tgz pyrobot; cd -; mv *.tgz download
	$(RM) -f download/pyrobot-latest.tgz
	cd download; ln -s pyrobot-$(PYROBOT_VERSION).tgz pyrobot-latest.tgz

Makefile.cfg:
	$(PYTHON_BIN) configure.py

bin/pyrobot: Makefile.cfg Makefile Makefile.src build/pyrobot
	echo "#!$(PYTHON_BIN)" > bin/pyrobot
	cat bin/pyrobot.py >> bin/pyrobot
	chmod a+x bin/pyrobot

clean:: 
	- $(RM) bin/pyrobot

