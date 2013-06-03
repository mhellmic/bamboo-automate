%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}

%if 0%{?rhel} == 5
%global with_python26 1
%endif

%if 0%{?with_python26}
%global __python26 %{_bindir}/python2.6
%global py26dir %{_builddir}/python26-%{name}-%{version}-%{release}
%{!?python26_sitelib: %global python26_sitelib %(%{__python26} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python26_sitearch: %global python26_sitearch %(%{__python26} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}
# Update rpm byte compilation script so that we get the modules compiled by the
# correct inerpreter
%global __os_install_post %__multiple_python_os_install_post
%endif

Name:		bamboo-automate
Version:	0.1
Release:	1%{?dist}
BuildArch:		noarch
Summary:	Python libraries to interact with a bamboo server
Group:		Applications/Internet
License:	ASL 2.0
URL:		https://github.com/mhellmic/bamboo-automate
Source0: https://github.com/mhellmic/bamboo-automate/archive/master.zip

BuildRequires:	cmake
%if 0%{?with_python26}
BuildRequires:	python26-devel
%else
BuildRequires:	python-devel
%endif

Requires: python-lxml

%description
This package provides a set of Python libraries to interact with an Atlassian Bamboo server. They use the bamboo REST API whenever possible, and otherwise go to the web frontend.

%prep
%setup -q -n %{name}-%{version}

%build
%cmake . -DCMAKE_INSTALL_PREFIX=/
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
make install DESTDIR=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitearch}/*

