include Config.mk

all: version.py
	bin/build.sh

tar: pyro-$(PYROVERSION).tgz

pyro-$(PYROVERSION).tgz: Makefile
	mv *.tgz tars/ || true
	make clean; cd ..; tar cfz pyro-$(PYROVERSION).tgz pyro --exclude CVS --exclude tars --exclude test --exclude examples/som --exclude som2 --exclude htmlsom --exclude experiments --exclude data --exclude kRobotClass --exclude simulator --exclude SIM --exclude stuff --exclude misc; mv pyro-$(PYROVERSION).tgz pyro; cd -; mv *.tgz tars

version.py: Makefile Config.mk
	echo -e "def version():\n\treturn \"$(PYROVERSION)\"" > system/version.py

clean:
	rm -rf `find . -name '*.pyc'`
	rm -rf `find . -name '*.pyo'`
	rm -rf `find . -name '*~'`
	rm -rf `find . -name '*.o'`
	rm -rf `find . -name '*.so'`
	rm -rf `find . -name '*.a'`
	bin/clean.sh

