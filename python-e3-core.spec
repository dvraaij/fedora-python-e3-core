# Upstream source information.
%global upstream_owner    AdaCore
%global upstream_name     e3-core
%global upstream_version  22.4.0
%global upstream_gittag   v%{upstream_version}

# Python Package Index name.
%global pypi_name %{upstream_name}

Name:           python-%{pypi_name}
Version:        %{upstream_version}
Release:        1%{?dist}
Summary:        Core framework for developing portable automated build systems

License:        GPL-3.0-only

URL:            https://github.com/%{upstream_owner}/%{upstream_name}
Source:         %{url}/archive/%{upstream_gittag}/%{upstream_name}-%{upstream_version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-tox
# GCC for recompiling the included `rlimit` tool.
BuildRequires:  gcc
# Git, Subversion and OpenSSL are required for some tests.
BuildRequires:  git
BuildRequires:  subversion
BuildRequires:  openssl

# [Fedora-specific] PyPI package `ld` is not available and seems obsolete, use `distro` instead.
Patch:          %{name}-replace-ld-by-distro.patch
# [Fedora-specific] Add the s390x and PowerPC platforms to the knowledge base.
Patch:          %{name}-adapt-knowledge-base-for-fedora.patch
# [Fedora-specific] We'll only package 1 recompiled version of `rlimit`.
Patch:          %{name}-single-rlimit-exec.patch
# [Fedora-specific] Use Python 3 for building the docs.
Patch:          %{name}-use-python3-for-building-the-docs.patch
# [Fedora-specific] PyPI packages `pytest-socket` and `pytest-html` are not (yet) available on Fedora.
Patch:          %{name}-pytest-socket-and-pytest-html-not-available.patch
# [Fedora-specific] Fix regression due to changes in the `typeguard` package.
Patch:          %{name}-fix-regression-typeguard.patch
# [Fedora-specific] PyPI packages `request-cache` currently available on Fedora is too old.
Patch:          %{name}-package-request-cache-is-too-old.patch
# [Fedora-specific] Set PROMPT_COMMAND environment variable in test.
Patch:          %{name}-set-prompt-command.patch
# [Python] 'nis' is deprecated and slated for removal in Python 3.13.
Patch:          %{name}-nis-is-deprecated.patch

%global common_description_en \
E3 is a Python framework to ease the development of portable automated build \
systems (compilation, dependency management, binary code packaging, and \
automated testing).

%description %{common_description_en}


#################
## Subpackages ##
#################

%package -n python3-%{pypi_name}
Summary:    %{summary}

%description -n python3-%{pypi_name} %{common_description_en}


#############
## Prepare ##
#############

%prep
%autosetup -n %{upstream_name}-%{upstream_version} -p1

# Remove all pre-compiled `rlimit` executables.
rm src/e3/os/data/rlimit*

# Emit some platform information that will be used to guess the host:
#
#   src/e3/platform_db/knowledge_base.py, HOST_GUESS
#
#   os  : uname -s
#   cpu : uname -m
#
uname -s
uname -m
gcc -dumpmachine


############################
## Generate BuildRequires ##
############################

%generate_buildrequires
%pyproject_buildrequires -t


###########
## Build ##
###########

%build

# Rebuild the `rlimit` executable.
%build_cc %{build_cflags} %{build_ldflags} -o src/e3/os/data/rlimit tools/rlimit/rlimit.c

# Build the package.
%pyproject_wheel

# Build the documentation.
# -- cannot build the docs: missing `sphinx-autoapi`
# make -C docs html


#############
## Install ##
#############

%install
%pyproject_install
%pyproject_save_files e3


###########
## Check ##
###########

%check

# The e3 script being tested is located in the /usr/bin folder relative to the buildroot.
sed --in-place \
    --expression='s,python_script("e3"),python_script("%{buildroot}%{_bindir}/e3"),' \
    tests/tests_e3/system/main_test.py
sed --in-place \
    --expression='s,python_script("e3-pypi-closure"),python_script("%{buildroot}%{_bindir}/e3-pypi-closure"),' \
    tests/tests_e3/python/main_test.py

%tox


###########
## Files ##
###########

%files -n python3-%{pypi_name} -f %pyproject_files
%license COPYING3
%doc README* NEWS*
%{_bindir}/e3
%{_bindir}/e3-sandbox
%{_bindir}/e3-pypi-closure
%{python3_sitelib}/e3_core-*-py3.*-nspkg.pth


###############
## Changelog ##
###############

%changelog
* Sun Jan 21 2024 Dennis van Raaij <dvraaij@fedoraproject.org> - 22.4.0-1
- Updated to v22.4.0.

* Sun Aug 6 2023 Dennis van Raaij <dvraaij@fedoraproject.org> - 22.2.0-3
- Fixed regression due to changes in the 'typeguard' package.

* Sat Oct 15 2022 Dennis van Raaij <dvraaij@fedoraproject.org> - 22.2.0-2
- Added the s390x and PowerPC platforms to the knowledge base.

* Sun Oct 02 2022 Dennis van Raaij <dvraaij@fedoraproject.org> - 22.2.0-1
- Updated to v22.2.0.

* Sun Sep 04 2022 Dennis van Raaij <dvraaij@fedoraproject.org> - 22.1.0-1
- New package.
