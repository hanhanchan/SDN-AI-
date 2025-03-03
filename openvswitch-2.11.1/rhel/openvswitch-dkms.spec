# Generated automatically -- do not modify!    -*- buffer-read-only: t -*-
# Spec file for Open vSwitch kernel modules using DKMS.
#
# Copyright (C) 2015 Nicira, Inc.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.

%define oname openvswitch

Name:             %{oname}-dkms
Version:          2.11.1
Release:          1%{?dist}
Summary:          Open vSwitch kernel module

Group:            System/Kernel
License:          GPLv2
URL:              http://openvswitch.org/
Source:           %{oname}-%{version}.tar.gz
Requires:         autoconf, gcc, make
Requires(post):   dkms
Requires(preun):  dkms
BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Without this we get an empty openvswitch-debuginfo package (whose name
# conflicts with the openvswitch-debuginfo package for OVS userspace).
%undefine _enable_debug_packages


%description
Open vSwitch Linux kernel module.


%prep
%setup -n %{oname}-%{version}

cat > %{oname}.conf << EOF
override %{oname} * extra/%{oname}
override %{oname} * weak-updates/%{oname}
EOF


%build
# for running the '%{__make} -C datapath print-build-modules' below.
./configure


%install
%{__rm} -rf %{buildroot}

# Kernel module sources install for dkms
%{__mkdir_p} %{buildroot}%{_usrsrc}/%{oname}-%{version}/
%{__cp} -r * %{buildroot}%{_usrsrc}/%{oname}-%{version}/

# check we can get kernel module names
%{__make} -C datapath print-build-modules

# Prepare dkms.conf
cat > %{buildroot}%{_usrsrc}/%{oname}-%{version}/dkms.conf << EOF
MODULES=( `%{__make} -C datapath print-build-modules | grep -v make` )

PACKAGE_NAME="openvswitch"
PACKAGE_VERSION="%{version}-%{release}"
MAKE="./configure --with-linux='\${kernel_source_dir}' && make -C datapath/linux"
for __idx in \${!MODULES[@]}; do
    BUILT_MODULE_NAME[__idx]=\${MODULES[__idx]}
    BUILT_MODULE_LOCATION[__idx]=datapath/linux/
    DEST_MODULE_LOCATION[__idx]=/kernel/drivers/net/openvswitch/
done
AUTOINSTALL=yes
EOF

install -d %{buildroot}%{_sysconfdir}/depmod.d/
install -m 644 %{oname}.conf %{buildroot}%{_sysconfdir}/depmod.d/


%post
# Add to DKMS registry
isadded=`dkms status -m "%{oname}" -v "%{version}"`
if [ "x${isadded}" = "x" ] ; then
    dkms add -m "%{oname}" -v "%{version}" || :
fi
dkms build -m "%{oname}" -v "%{version}" || :
dkms install -m "%{oname}" -v "%{version}" --force || :


%preun
# Remove all versions from DKMS registry
dkms remove -m "%{oname}" -v "%{version}" --all || :


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root)
%{_usrsrc}/%{oname}-%{version}/
/etc/depmod.d/openvswitch.conf
