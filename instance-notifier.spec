%global with_doc 0

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif


Name:             instance-notifier
Version:          0.1
Release:          1
Summary:          Fping notifier server
License:          GNU LGPL 2.1
Vendor:           Grid Dynamics International, Inc.
URL:              http://www.griddynamics.com/openstack
Group:            Development/Languages/Python

Source0:          %{name}-%{version}.tar.gz
BuildRoot:        %{_tmppath}/%{name}-%{version}-build
BuildRequires:    python-devel python-setuptools make
BuildArch:        noarch
Requires:         python-jinja2
Requires:         python-openstackclient-base-essex
Requires:         python-novaclient-essex
Requires:         python-keystoneclient-essex

Requires:         start-stop-daemon


%description


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
%__rm -rf %{buildroot}

%{__python} setup.py install -O1 --skip-build --prefix=%{_prefix} --root=%{buildroot}
install -p -d -m755 %{buildroot}%{_datarootdir}/%{name}

cd redhat
for script in *.init; do
    install -p -D -m 755 "$script" "%{buildroot}%{_initrddir}/${script%.init}"
done
cd ..
mkdir -p %{buildroot}/etc/
cp -a etc %{buildroot}/etc/instance-notifier
mkdir -p %{buildroot}%{_localstatedir}/{log,lib,run}/instance-notifier


%clean
%__rm -rf %{buildroot}


%pre
getent group focus >/dev/null || groupadd -r focus
getent passwd focus >/dev/null || \
useradd -r -g focus -d %{_sharedstatedir}/focus -s /sbin/nologin \
-c "Focus Daemon" focus
exit 0


%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
exit 0


%postun
if [ $1 -eq 1 ] ; then
    /sbin/service %{name} condrestart
fi
exit 0


%files
%defattr(-,root,root,-)
%doc README.rst
%{_initrddir}/*
%{python_sitelib}/*
%{_usr}/bin/*

%defattr(-,focus,focus,-)
%config(noreplace) /etc/instance-notifier/*

%defattr(0775,focus,focus,-)
%dir %{_sharedstatedir}/instance-notifier
%dir %{_localstatedir}/log/instance-notifier
%dir %{_localstatedir}/run/instance-notifier


%changelog
