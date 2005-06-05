# Pyrobot RPM SPEC File

%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.3)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Python Robotics, toolkit for exploring AI and robotics
Name: pyrobot
Version: 4.0.2
Release: 1
Group: Application
License: GPL
URL: http://PyroRobotics.org/
Source: http://PyroRobotics.org/download/%{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Requires: python >= %{pythonver}, python-imaging, python-tkinter
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
./configure.py --defaults --prefix=%{_prefix}
make

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
* Sun May 22 2005 Douglas Blank <dblank@brynmawr.edu> - 
- Initial build.

