# Pyrobot RPM SPEC File

#%_topdir /home/your_userid/rpm
#cd /home/your_userid/rpm
#mkdir SOURCES SPECS BUILD SRPMS
#mkdir -p RPMS/i386 RPMS/athlon RPMS/i486 RPMS/i586 RPMS/i686 RPMS/noarch

%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.3)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Python Robotics, toolkit for explore AI and robotics
Name: pyrobot
Version: 4.0.0
Release: 1
Group: Education/Robotics
License: GPL
URL: http://PyroRobotics.org/
Source: http://PyroRobotics.org/tars/%{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Requires: python >= %{pythonver}
BuildRequires: python, python-devel
Obsoletes: pyrobot <= %{version}
Provides: pyrobot = %{version}-%{release}

%description
Python Robotics is designed to explore robotics in education
and research. It has an easy to use interface for connecting
onto real and simulated robots, including AIBO, Robocup Soccer
server, Player/Stage/Gazebo, and others.

%prep
%setup -q -n pyrobot

%build
./configure 

%install
%{__rm} -rf %{buildroot}
install -d %{pythondir}/pyrobot/
cp -r * %{pythondir}/pyrobot/
install bin/pyrobot %{_bindir}
install bin/ipyrobot %{_bindir}

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
#%doc CHANGES* CONTENTS README Images/ Sane/ Scripts/
%{_libdir}/python*/site-packages/pyrobot/
%{_bindir}/pyrobot
%{_bindir}/ipyrobot

%changelog
* Sun May 22 2005 Douglas Blank <dblank@saliva.brynmawr.edu> - 
- Initial build.

