# Makefile.in generated automatically by automake 1.4-p5 from Makefile.am

# Copyright (C) 1994, 1995-8, 1999, 2001 Free Software Foundation, Inc.
# This Makefile.in is free software; the Free Software Foundation
# gives unlimited permission to copy and/or distribute it,
# with or without modifications, as long as this notice is preserved.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, to the extent permitted by law; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.


SHELL = /bin/sh

srcdir = .
top_srcdir = ..

prefix = /usr/local
exec_prefix = ${prefix}

bindir = ${exec_prefix}/bin
sbindir = ${exec_prefix}/sbin
libexecdir = ${exec_prefix}/libexec
datadir = ${prefix}/share
sysconfdir = ${prefix}/etc
sharedstatedir = ${prefix}/com
localstatedir = ${prefix}/var
libdir = ${exec_prefix}/lib
infodir = ${prefix}/info
mandir = ${prefix}/man
includedir = ${prefix}/include
oldincludedir = /usr/include

DESTDIR =

pkgdatadir = $(datadir)/gazebo-src
pkglibdir = $(libdir)/gazebo-src
pkgincludedir = $(includedir)/gazebo-src

top_builddir = ..

ACLOCAL = aclocal
AUTOCONF = autoconf
AUTOMAKE = automake
AUTOHEADER = autoheader

INSTALL = /usr/bin/install -c
INSTALL_PROGRAM = ${INSTALL} $(AM_INSTALL_PROGRAM_FLAGS)
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_SCRIPT = ${INSTALL}
transform = s,x,x,

NORMAL_INSTALL = :
PRE_INSTALL = :
POST_INSTALL = :
NORMAL_UNINSTALL = :
PRE_UNINSTALL = :
POST_UNINSTALL = :
build_alias = 
build_triplet = i686-pc-linux-gnu
host_alias = 
host_triplet = i686-pc-linux-gnu
target_alias = 
target_triplet = i686-pc-linux-gnu
CC = gcc
CPP = gcc -E
CXX = g++
GAZEBO_MODEL_CPPFLAGS = -I$(top_srcdir)/server -I$(top_srcdir)/server/bodies -I$(top_srcdir)/toolkit -I$(top_srcdir)/libgazebo `xml2-config --cflags`
GAZEBO_MODEL_EXTRA_LIBS =                        
GAZEBO_MODEL_LIBPATHS =  models/AvatarHeli/libavatarheli.a  models/ClodBuster/libclodbuster.a models/Factory/libfactory.a models/GarminGPS/libgarmingps.a models/GroundPlane/libgroundplane.a models/LightSource/liblightsource.a  models/Pioneer2AT/libpioneer2at.a models/Pioneer2DX/libpioneer2dx.a models/PointSet/libpointset.a models/SegwayRMP/libsegwayrmp.a  models/SickLMS200/libsicklms200.a models/SimpleSolid/libsimplesolid.a models/SonyVID30/libsonyvid30.a  models/TotemPole/libtotempole.a models/TruthWidget/libtruthwidget.a  models/Pioneer2Gripper/libpioneer2gripper.a models/Pioneer2Sonars/libpioneer2sonars.a models/ObserverCam/libobservercam.a
GAZEBO_MODEL_LIBS =  libavatarheli.a  libclodbuster.a libfactory.a libgarmingps.a libgroundplane.a liblightsource.a  libpioneer2at.a libpioneer2dx.a libpointset.a libsegwayrmp.a  libsicklms200.a libsimplesolid.a libsonyvid30.a  libtotempole.a libtruthwidget.a  libpioneer2gripper.a libpioneer2sonars.a libobservercam.a
GAZEBO_SENSOR_CPPFLAGS = -I/usr/include/libxml2
GAZEBO_SENSOR_EXTRA_LIBS =    
GAZEBO_SENSOR_LIBPATHS =  sensors/Camera/libcamera.a sensors/RayProximity/librayproximity.a 
GAZEBO_SENSOR_LIBS =  libcamera.a librayproximity.a 
GL_CPPFLAGS = 
GL_LDADD = -lGL -lGLU -lglut
MAKEINFO = makeinfo
ODE_CPPFLAGS = 
ODE_LDADD = -lode
OPCODE_CPPFLAGS = 
OPCODE_ENABLED = no
OPCODE_LDADD = 
OSG_CPPFLAGS = @OSG_CPPFLAGS@
OSG_LDADD = @OSG_LDADD@
PACKAGE = gazebo-src
RANLIB = ranlib
VERSION = 0.4.0
XML_CPPFLAGS = -I/usr/include/libxml2
XML_LDADD = -L/usr/lib -lxml2 -lz -lm
have_xml2 = yes
name_caps = @name_caps@
other_name_caps = @other_name_caps@

configdir = $(prefix)/share/gazebo/worlds

WORLDFILES = example1.world example2.world segwayrmp.world pioneer2at.world 						 pioneer2dx.world clodbuster.world pioneer2dxGrip.world 						 pioneer2dxSonars.world simplesolids.world textures.world terrain.world


CONFIGFILES = pioneer2dx.config pioneer2dxGrip.config pioneer2dxSonars.config

TEXTUREFILES = ahoward.jpg nkoenig.jpg grass.jpg ground.ppm sky.ppm wood.ppm example2.png 							 grid.ppm terrain.png


config_DATA = $(WORLDFILES) $(CONFIGFILES) $(TEXTUREFILES)

EXTRA_DIST = $(WORLDFILES) $(CONFIGFILES) $(TEXTUREFILES)
mkinstalldirs = $(SHELL) $(top_srcdir)/mkinstalldirs
CONFIG_HEADER = ../config.h
CONFIG_CLEAN_FILES = 
DATA =  $(config_DATA)

DIST_COMMON =  Makefile.am Makefile.in


DISTFILES = $(DIST_COMMON) $(SOURCES) $(HEADERS) $(TEXINFOS) $(EXTRA_DIST)

TAR = tar
GZIP_ENV = --best
all: all-redirect
.SUFFIXES:
$(srcdir)/Makefile.in: Makefile.am $(top_srcdir)/configure.in $(ACLOCAL_M4) 
	cd $(top_srcdir) && $(AUTOMAKE) --gnu --include-deps worlds/Makefile

Makefile: $(srcdir)/Makefile.in  $(top_builddir)/config.status
	cd $(top_builddir) \
	  && CONFIG_FILES=$(subdir)/$@ CONFIG_HEADERS= $(SHELL) ./config.status


install-configDATA: $(config_DATA)
	@$(NORMAL_INSTALL)
	$(mkinstalldirs) $(DESTDIR)$(configdir)
	@list='$(config_DATA)'; for p in $$list; do \
	  if test -f $(srcdir)/$$p; then \
	    echo " $(INSTALL_DATA) $(srcdir)/$$p $(DESTDIR)$(configdir)/$$p"; \
	    $(INSTALL_DATA) $(srcdir)/$$p $(DESTDIR)$(configdir)/$$p; \
	  else if test -f $$p; then \
	    echo " $(INSTALL_DATA) $$p $(DESTDIR)$(configdir)/$$p"; \
	    $(INSTALL_DATA) $$p $(DESTDIR)$(configdir)/$$p; \
	  fi; fi; \
	done

uninstall-configDATA:
	@$(NORMAL_UNINSTALL)
	list='$(config_DATA)'; for p in $$list; do \
	  rm -f $(DESTDIR)$(configdir)/$$p; \
	done
tags: TAGS
TAGS:


distdir = $(top_builddir)/$(PACKAGE)-$(VERSION)/$(subdir)

subdir = worlds

distdir: $(DISTFILES)
	@for file in $(DISTFILES); do \
	  d=$(srcdir); \
	  if test -d $$d/$$file; then \
	    cp -pr $$d/$$file $(distdir)/$$file; \
	  else \
	    test -f $(distdir)/$$file \
	    || ln $$d/$$file $(distdir)/$$file 2> /dev/null \
	    || cp -p $$d/$$file $(distdir)/$$file || :; \
	  fi; \
	done
info-am:
info: info-am
dvi-am:
dvi: dvi-am
check-am: all-am
check: check-am
installcheck-am:
installcheck: installcheck-am
install-exec-am:
install-exec: install-exec-am

install-data-am: install-configDATA
install-data: install-data-am

install-am: all-am
	@$(MAKE) $(AM_MAKEFLAGS) install-exec-am install-data-am
install: install-am
uninstall-am: uninstall-configDATA
uninstall: uninstall-am
all-am: Makefile $(DATA)
all-redirect: all-am
install-strip:
	$(MAKE) $(AM_MAKEFLAGS) AM_INSTALL_PROGRAM_FLAGS=-s install
installdirs:
	$(mkinstalldirs)  $(DESTDIR)$(configdir)


mostlyclean-generic:

clean-generic:

distclean-generic:
	-rm -f Makefile $(CONFIG_CLEAN_FILES)
	-rm -f config.cache config.log stamp-h stamp-h[0-9]*

maintainer-clean-generic:
mostlyclean-am:  mostlyclean-generic

mostlyclean: mostlyclean-am

clean-am:  clean-generic mostlyclean-am

clean: clean-am

distclean-am:  distclean-generic clean-am

distclean: distclean-am

maintainer-clean-am:  maintainer-clean-generic distclean-am
	@echo "This command is intended for maintainers to use;"
	@echo "it deletes files that may require special tools to rebuild."

maintainer-clean: maintainer-clean-am

.PHONY: uninstall-configDATA install-configDATA tags distdir info-am \
info dvi-am dvi check check-am installcheck-am installcheck \
install-exec-am install-exec install-data-am install-data install-am \
install uninstall-am uninstall all-redirect all-am all installdirs \
mostlyclean-generic distclean-generic clean-generic \
maintainer-clean-generic clean mostlyclean distclean maintainer-clean


# Tell versions [3.59,3.63) of GNU make to not export all variables.
# Otherwise a system limit (for SysV at least) may be exceeded.
.NOEXPORT:
