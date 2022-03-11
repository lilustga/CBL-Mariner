%define upstream_name moby
%define commit_hash 459d0dfbbb51fb2423a43655e6c62368ec0f36c9

Summary: The open-source application container engine
Name:    %{upstream_name}-engine
Version: 20.10.12
Release: 2%{?dist}
License: ASL 2.0
Group:   Tools/Container
URL: https://mobyproject.org
Vendor: Microsoft Corporation
Distribution: Mariner

Source0: https://github.com/moby/moby/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# docker-proxy binary comes from libnetwork
# - The libnetwork version (more accurately commit hash) 
#   that moby relies on is hard coded in 
#   "hack/dockerfile/install/proxy.installer" (in moby github repo above)
Source1: https://github.com/moby/libnetwork/archive/master.tar.gz/#/%{upstream_name}-libnetwork-%{version}.tar.gz
Source3: docker.service
Source4: docker.socket

%{?systemd_requires}

BuildRequires: bash
BuildRequires: btrfs-progs-devel
BuildRequires: cmake
BuildRequires: device-mapper-devel
BuildRequires: gcc
BuildRequires: glibc-devel
BuildRequires: libseccomp-devel
BuildRequires: libselinux-devel
BuildRequires: libtool
BuildRequires: libltdl-devel
BuildRequires: make
BuildRequires: pkg-config
BuildRequires: systemd-devel
BuildRequires: tar
BuildRequires: golang >= 1.16.12
BuildRequires: git

Requires: audit
Requires: /bin/sh
Requires: device-mapper-libs >= 1.02.90-1
Requires: docker-init
Requires: iptables
Requires: libcgroup
Requires: libseccomp >= 2.3
Requires: moby-containerd >= 1.2
Requires: tar
Requires: xz

Conflicts: docker
Conflicts: docker-io
Conflicts: docker-engine-cs
Conflicts: docker-ee

Obsoletes: docker-ce
Obsoletes: docker-engine
Obsoletes: docker
Obsoletes: docker-io

%description
Moby is an open-source project created by Docker to enable and accelerate software containerization.

%define OUR_GOPATH %{_topdir}/.gopath

%prep
%autosetup -p1 -n %{upstream_name}-%{version}
tar xf %{SOURCE1} --no-same-owner

mkdir -p %{OUR_GOPATH}/src/github.com/docker
LIBNETWORK_FOLDER=$(find -type d -name "libnetwork-*")
ln -sfT %{_builddir}/%{upstream_name}-%{version}/${LIBNETWORK_FOLDER} %{OUR_GOPATH}/src/github.com/docker/libnetwork
ln -sfT %{_builddir}/%{upstream_name}-%{version} %{OUR_GOPATH}/src/github.com/docker/docker

%build
export GOPATH=%{OUR_GOPATH}
export GOCACHE=%{OUR_GOPATH}/.cache
export GOPROXY=off
export GO111MODULE=off
export GOGC=off
export VERSION=%{version}

# build docker daemon
GIT_COMMIT=%{commit_hash}
GIT_COMMIT_SHORT=${GIT_COMMIT:0:7}
DOCKER_GITCOMMIT=${GIT_COMMIT_SHORT} DOCKER_BUILDTAGS='apparmor seccomp' hack/make.sh dynbinary

# build docker proxy
go build \
    -o libnetwork/docker-proxy \
    github.com/docker/libnetwork/cmd/proxy

%install
mkdir -p %{buildroot}/%{_bindir}
cp -aLT ./bundles/dynbinary-daemon/dockerd %{buildroot}/%{_bindir}/dockerd
cp -aT libnetwork/docker-proxy %{buildroot}/%{_bindir}/docker-proxy

# install udev rules
mkdir -p %{buildroot}/%{_sysconfdir}/udev/rules.d
install -p -m 644 contrib/udev/80-docker.rules %{buildroot}/%{_sysconfdir}/udev/rules.d/80-docker.rules

# add init scripts
mkdir -p %{buildroot}/%{_unitdir}
install -p -m 644 %{SOURCE3} %{buildroot}/%{_unitdir}/docker.service
install -p -m 644 %{SOURCE4} %{buildroot}/%{_unitdir}/docker.socket

%post
if ! grep -q "^docker:" /etc/group; then
	groupadd --system docker
fi

%preun
%systemd_preun docker.service

%postun
%systemd_postun_with_restart docker.service

# list files owned by the package here
%files
%license LICENSE NOTICE
%{_bindir}/*
%{_sysconfdir}/*
%{_unitdir}/*

%changelog
* Wed Mar 02 2022 Andy Caldwell <andycaldwell@microsoft.com> - 20.10.12-2
- Relax dependency from `tini` to `docker-init`

* Fri Feb 04 2022 Nicolas Guibourge <nicolasg@microsoft.com> - 20.10.12-1
- Update to version 20.10.12
- Use code from upstream instead of Azure fork.

* Mon Oct 04 2021 Henry Beberman <henry.beberman@microsoft.com> 19.03.15+azure-4
- Patch CVE-2021-41091 and CVE-2021-41089
- Switch to autosetup

* Fri Aug 06 2021 Nicolas Guibourge <nicolasg@microsoft.com> 19.03.15+azure-3
- Increment release to force republishing using golang 1.16.7.

* Tue Jun 08 2021 Henry Beberman <henry.beberman@microsoft.com> 19.03.15+azure-2
- Increment release to force republishing using golang 1.15.13.

* Thu Apr 15 2021 Andrew Phelps <anphel@microsoft.com> 19.03.15+azure-1
- Update to version 19.03.15+azure

* Thu Dec 10 2020 Andrew Phelps <anphel@microsoft.com> 19.03.11+azure-4
- Increment release to force republishing using golang 1.15.

* Tue Jul 21 2020 Nicolas Ontiveros <niontive@microsoft.com> 19.03.11+azure-3
- Remove changes for CIS Docker Security Benchmark compliance.

* Fri Jul 03 2020 Chris Co <chrco@microsoft.com> 19.03.11+azure-2
- Remove default daemon configuration

* Thu Jun 11 2020 Andrew Phelps <anphel@microsoft.com> 19.03.11+azure-1
- Update to version 19.03.11+azure

* Thu May 28 2020 Nicolas Ontiveros <niontive@microsoft.com> 3.0.12~rc.1+azure-8
- Make default configuration comply with CIS Docker Security Benchmark.

* Wed May 20 2020 Joe Schmitt <joschmit@microsoft.com> 3.0.12~rc.1+azure-7
- Remove reliance on existing GOPATH environment variable.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 3.0.12~rc.1+azure-6
- Added %%license line automatically

* Fri May 08 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 3.0.12~rc.1+azure-5
- Removing *Requires for "ca-certificates".
- Removing duplicate %%files directive.

* Fri May 08 2020 Eric Li <eli@microsoft.com> 3.0.12~rc.1+azure-4
- Add #Source0: and license verified

* Wed May 06 2020 Mohan Datla <mdatla@microsoft.com> 3.0.12~rc.1+azure-3
- Fixing the moby server version

* Fri May 01 2020 Emre Girgin <mrgirgin@microsoft.com> 3.0.12~rc.1+azure-2
- Renaming go to golang

* Fri Apr 03 2020 Mohan Datla <mdatla@microsoft.com> 3.0.12~rc.1+azure-1
- Initial CBL-Mariner import from Azure.

* Mon Jan 27 2020 Brian Goffs <brgoff@microsoft.com>
- Use dynamic linking and issue build commands from rpm spec

* Tue Aug 7 2018 Robledo Pontes <rafilho@microsoft.com>
- Adding to moby build tools.

* Mon Mar 12 2018 Xing Wu <xingwu@microsoft.com>
- First draft
