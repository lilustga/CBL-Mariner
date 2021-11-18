Summary:        Modern C++11 JSON library
Name:           nlohmann-json
Version:        3.10.4
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment
URL:            https://github.com/nlohmann/json
#Source0:       https://github.com/nlohmann/json/archive/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz
%global debug_package %{nil}
BuildRequires:  cmake
BuildRequires:  gcc

%description
A modern C++ JSON library.

%package devel
Summary:        Development files for %{name}

%description devel
Development files for %{name}

%prep
%setup -q -n json-%{version}

%build
mkdir build && cd build
%cmake ..
%make_build

%check
make test -C build

%install
%make_install -C build

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files devel
%defattr(-,root,root)
%license LICENSE.MIT
%doc README.md
%{_includedir}/nlohmann
%{_libdir}/cmake/nlohmann_json
%{_libdir}/pkgconfig/nlohmann_json.pc

%changelog
* Wed Nov 10 2021 Pawel Winogrodzki <pawel.winogrodzki@microsoft.com> - 3.10.4-1
- Updating to version 3.10.4 to get code fixes for GCC 10 and 11.

* Mon Oct 12 2020 Thomas Crain <thcrain@microsoft.com> - 3.6.1-2
- Update Source0
- License verified

* Tue Feb 11 2020 Nick Bopp <nichbop@microsoft.com> - 3.6.1-1
- Original version for CBL-Mariner.
