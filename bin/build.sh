#!/bin/bash

# script to build all C in pyro
#
#this program expects to be run in root pyro directory
#
# - stephen -
#
#
# TODO:
# 	Add optional builds for optional packages like saphira
#	Add proper error return checking

#. bin/environment.sh

MAKEFILES=`find . -name Makefile`

echo Building $MAKEFILES

for x in $MAKEFILES;
do
	if [ $x != './Makefile' ]; then
		make -C `dirname $x`
	fi
done;
