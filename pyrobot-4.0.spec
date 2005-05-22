Summary: Python Robotics, toolkit for explore AI and robotics
Name: pyrobot
Version: 4.0.0
Release: 1
#License: GPL
Copyright: 2000 - 2005, D.S. Blank
Group: Education/Robotics
URL: http://PyroRobotics.org/
Source: http://PyroRobotics.org/tars/%{name}-%{version}.tgz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Vendor: Bryn Mawr College
Packager: D.S. Blank <dblank@cs.brynmawr.edu>

%description
Python Robotics is designed to explore robotics in education
and research. It has an easy to use interface for connecting
onto real and simulated robots, including AIBO, Robocup Soccer
server, Player/Stage/Gazebo, and others.

%prep
%setup 

%build
make

%install
rm -rf $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc

%changelog
* Sun May 22 2005 Douglas Blank <dblank@saliva.brynmawr.edu> - 
- Initial build.

