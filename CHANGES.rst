################
Racker changelog
################


in progress
===========

- Increase resources assigned to Vagrant environment.
  Now, it gets 4 VCPUs and 4096 MB RAM.
- Improve platform guards and naming things
- Improve central command invocation function
- Improve documentation
- Make Windows runner subsystem production ready.
- Add support for Windows Server Core 2019 and friends, like
  ``windows/servercore:ltsc2019``, ``windows/nanoserver:1809``, or
  ``eclipse-temurin:17-jdk``.
- Add support for Windows Server Core 2016, 2022 and friends, like
  ``windows/servercore:ltsc2016``, ``windows/servercore:ltsc2022``, or
  ``windows/nanoserver:ltsc2022``.
- Improve documentation about the Windows backend
- Rename environment variables used to control the Windows Docker Machine
  subsystem. The new names are ``RACKER_WDM_VCPUS``, ``RACKER_WDM_MEMORY``,
  and ``RACKER_WDM_MACHINE``.
- Add environment variable ``RACKER_WDM_PROVIDER`` to reconfigure the
  Vagrant virtualization backend differently than VirtualBox.
- Documentation: Add use case how to build a Python package within a
  Windows environment, using Microsoft Visual C++ Build Tools 2015 and
  Anaconda, both installed using Chocolatey, and ``cibuildwheel``.


2022-05-20 0.2.0
================

- Add software tests to CI/GHA
- Naming things: Add ``racker`` command with ``racker {pull,run}`` subcommands
- Improve subprocess stdout/stderr redirection and error handling
- Activate full ``umoci``-unpacked images
- Add test case for ``postroj pkgprobe``
- Improve image subsystem to acquire arbitrary Docker filesystem images
- Add operating system support for SLES 15, SLES BCI, RHEL, CentOS 9
- Add operating system support for RHEL UBI's "minimal" flavors
- Add custom exception objects
- Add more test cases to raise code coverage to >75%
- Refactoring: Bundle ``systemd-nspawn``/``machinectl`` to ``postroj.backend.nspawn``
- Refactoring: Move code from ``setup_ubuntu`` to generic ``acquire_from_http``


2022-05-08 0.1.0
================

- Add ``ImageProvider`` implementation to provision operating system images
- Add resources and documentation for sandbox setup based on Vagrant
- Supported operating systems:
  Debian, Ubuntu, Fedora, openSUSE, Arch Linux,
  CentOS, Rocky Linux, Amazon Linux, Oracle Linux
- Add basic probing for unit ``systemd-journald``
- Add example probe implementation for the Apache web server
- Add ``postroj pkgprobe`` implementation
- Add ``postroj list-images`` subcommand
- Add caching of download artefacts
- Improve robustness and documentation
- Add subcommand ``postroj pull [--all]``
- Add subcommand ``postroj selftest {hostnamectl,pkgprobe}``
- Improve process management of container wrapper
- Generalize process wrapper for launching Nspawn containers
- Add subcommand ``postroj run``
- Fix ``stty: 'standard input': Inappropriate ioctl for device``
- Refactor application settings
- Add software test framework and basic tests for ``postroj run``
- Refactor data model for curated operating systems / disk images
- Allow ``versionname`` labels like ``debian-11`` for addressing curated filesystem images
- Rename project to *Racker* and Python package to ``racker``


2022-03-16 0.0.0
================

- Add convenience wrapper around ``systemd-nspawn``
- Add convenience wrapper around Windows Docker Machine
