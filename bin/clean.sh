#!/bin/bash

# script to clean all C builds in pyro
#
# this program expects to be run in root pyro directory
#
# - stephen -


. bin/environment.sh

MAKEFILES=`find . -name Makefile`


for x in $MAKEFILES;
do
	if [ $x != './Makefile' ]; then
		make -C `dirname $x` clean
	fi
done;
