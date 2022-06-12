######################
Racker Windows backend
######################


*****
About
*****

Launch an interactive command prompt (cmd, PowerShell, or Bash) within a
Windows environment (2016, 2019, or 2022) or invoke programs
non-interactively.

Features
========

- The subsystem is heavily based on the excellent `Windows Docker Machine`_.
- The package manager `Chocolatey`_ is pre-installed on the container images
  where PowerShell is available.
- Programs like ``busybox``, ``curl``, ``git``, ``nano``, and ``wget`` are
  pre-installed on the container images where `Chocolatey`_ is available.
- The `Windows container version compatibility`_ problem is conveniently
  solved by automatically selecting the right machine matching the requested
  container image.


Use cases
=========

The first encounter with `Windows Docker Machine`_ was when aiming to run the
build process of the PyTables Python package within a Windows environment, see
`Wheels for Windows`_.

The second use case was to run the Java test suite of CrateDB within a Windows
environment, see `Using Racker and Postroj for CrateDB CI`_.




*****
Setup
*****
::

    # Install VirtualBox, Vagrant, Docker, Python, and Racker.
    brew install virtualbox vagrant docker python
    pip install racker


********
Synopsis
********
::

    racker --verbose run --rm \
        --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019 -- \
        wmic os get caption


*************
Configuration
*************

Resources
=========

When creating the `Windows Docker Machine`_ virtual machine, the program will
configure it to use 4 VCPUs and 4 GB system memory by default.

In order to adjust those values, use these environment variables before
invoking the later commands::

    export RACKER_WDM_VCPUS=8
    export RACKER_WDM_MEMORY=8192

If you want to adjust the values after the initial deployment, you will have to
reset the `Windows Docker Machine`_ installation directory. For example, it is:

- On Linux: ``/root/.local/state/racker/windows-docker-machine``
- On macOS: ``/Users/amo/Library/Application Support/racker/windows-docker-machine``


VM provider
===========

`Vagrant`_ is able to use different providers as virtualization backend. By
default, Racker selects `VirtualBox`_. In order to change the backend,
reconfigure this environment variable::

    export RACKER_WDM_PROVIDER=vmware_workstation

Possible values are, in alphabetical order, ``hyperv``, ``virtualbox``,
``qemu``, ``vmware_fusion``, ``vmware_workstation``.

Please note that this has not been tested with providers other than
`VirtualBox`_, so we would welcome to receive feedback from the community
whether this also works well for them on other hypervisors.


VM machine
==========

The architecture of Windows leads to container compatibility requirements that
are different than on Linux, more background about this detail can be found at
`Windows container version compatibility`_.

In order to provide appropriate convenience, Racker's launcher subsystem
inquires the ``os.version`` attribute of the OCI image about the designated
version of Windows version before starting the container. Based on the version,
the corresponding Windows Docker Machine host is selected to run the payload
on. Currently, the supported operating systems are Windows 2016, 2019, and 2022.

Certain container images can still be launched on mismatching operating system
versions, for example, the `eclipse-temurin`_ container images. By default,
when possible, the image will be launched on a Windows 2022 machine. If you
want to explicitly control on which runner host the container will be launched,
use another environment variable::

    export RACKER_WDM_MACHINE=2019-box

If you receive error messages like ``docker: no matching manifest for
windows/amd64 10.0.17763 in the manifest list entries.``, reset this setting
by typing::

    unset RACKER_WDM_MACHINE

Vagrant stores the boxes in this directory:

- On Linux an macOS: ``~/.vagrant.d/boxes``
- On Windows: ``C:/Users/USERNAME/.vagrant.d/boxes``

The sizes of the three Vagrant boxes are:

- ``StefanScherer/windows_2016_docker``: 11.0 GB
- ``StefanScherer/windows_2019_docker``: 14.0 GB
- ``StefanScherer/windows_2022_docker``:  6.4 GB


********
Examples
********


Introduction
============

For understanding some of the acronyms used in the following section, it is
good to memorize those:

- LTSC: Long-Term Servicing Channel
- SAC: Semi-Annual Channel

For more details, see `Overview of System Center release options`_.


Choosing a base image
=====================

Quoting from `Windows Container Base Images`_:

    How do you choose the right base image to build upon? For most users, Windows
    Server Core and Nanoserver will be the most appropriate image to use. Each
    base image is briefly described below:

    - ``Nano Server`` is an ultralight Windows offering for new application
      development.
    - ``Server Core`` is medium in size and a good option for "lifting and
      shifting" Windows Server apps.
    - ``Windows Server`` has full Windows API support, and allows you to use
      more server features.
    - ``Windows`` is the largest image and has full Windows API support for
      workloads.

The examples outlined within this section will use different Windows container
images. According to the feature set outlined above, their download sizes are
different.

- Nano Server: 125 MB
- Server Core: 2.2 GB
- Windows Server: 4.8 GB
- Windows: 7.1 GB


System information
==================

Install and run `Winfetch`_::

    racker --verbose run --rm \
        --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2022 -- \
        cmd /C 'choco install --yes --force winfetch & refreshenv & winfetch'

.. figure:: https://user-images.githubusercontent.com/453543/173195228-b75c8727-7187-4c38-ae28-f74098dfb450.png
    :width: 800

With ``ver``, ``reg``, WMI and PowerShell::

    # Both ``ver`` and ``reg`` will be available even on Nano Server.
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2016 -- cmd /C ver
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2016 -- 'reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName'
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2016 -- 'reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v InstallationType'

    # WMI and PowerShell are not always available.
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2016 -- wmic os get caption
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019 -- powershell -Command Get-ComputerInfo
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2022 -- powershell -Command Get-ComputerInfo -Property WindowsProductName

With ``busybox``::

    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2022 -- cmd

    C:\>busybox nproc
    6

    C:\>busybox free -m
                  total        used        free      shared  buff/cache   available
    Mem:           2048        1422    16774251           0        3591           0
    Swap:          1664           0        1664

    C:\>busybox df -h
    Filesystem                Size      Used Available Use% Mounted on
    C:                       19.9G     83.3M     19.8G   0% C:/


Interactive command prompt
==========================

Where possible, the operating system images offer three terminal/shell
programs: cmd, PowerShell, and Bash. To get an interactive shell, run::

    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2016 cmd
    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019 powershell
    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2022 bash


Invoke single command
=====================
::

    # Run a basic command with cmd, PowerShell, and Bash.
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2016 cmd /C echo "Hello, world."
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019 -- 'powershell -Command {echo "Hello, world."}'
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2022 'sh -c "echo Hello, world."'

    # Use stdin and stdout, with time keeping.
    time racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:1809 cmd /C echo "Hello, world." > hello
    cat hello


Nano Server
===========
::

    # Display system version.
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:sac2016 cmd /C ver
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:1809 cmd /C ver
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:ltsc2022 cmd /C ver

    # Interactive shell with cmd.
    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:1809 cmd

    # Interactive shell with PowerShell.
    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/powershell:nanoserver-ltsc2022 pwsh


Windows Server
==============
::

    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/server:ltsc2022 -- cmd /C ver
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/server:ltsc2022 -- wmic os get caption
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/server:ltsc2022 -- powershell -Command Get-ComputerInfo -Property WindowsProductName


Windows
=======
::

    # Windows 10
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows:1809 -- cmd /C ver
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows:1809 -- wmic os get caption
    racker --verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows:1809 -- powershell -Command Get-ComputerInfo -Property WindowsProductName

    # Untested.
    racker --verbose run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows:20H2 wmic os get caption


Midnight Commander
==================

Install and run `Midnight Commander`_::

    racker --verbose run -it --rm \
        --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2022 -- \
        cmd /C 'choco install --yes --force mc --install-arguments=/tasks=modifypath & refreshenv & mc'

.. figure:: https://user-images.githubusercontent.com/453543/173195789-9ef87618-5526-4317-99d7-b0dee6ca3970.png
    :width: 800


Python
======

Select a Windows container image including `Python`_ and launch it.

Display Python version, launched within containers in different environments::

    # Server Core
    racker --verbose run --rm --platform=windows/amd64 python:2.7 -- python -V
    racker --verbose run --rm --platform=windows/amd64 python:3.9 -- python -V
    racker run --rm --platform=windows/amd64 winamd64/python:3.9-windowsservercore-1809 -- python -V
    racker run --rm --platform=windows/amd64 winamd64/python:3.10-windowsservercore-ltsc2022 -- python -V
    racker run --rm --platform=windows/amd64 winamd64/python:3.11-rc -- python -V

    # Explicitly select `2019-box` as different host OS.
    # The default would be to automatically select `2022-box`.
    RACKER_WDM_MACHINE=2019-box racker --verbose run --rm --platform=windows/amd64 winamd64/python:3.11-rc -- python -V

    # Nano Server
    racker --verbose run --rm --platform=windows/amd64 stefanscherer/python-windows:nano -- python -V

Display the Zen of Python::

    racker --verbose run --rm --platform=windows/amd64 python:3.9 -- 'python -c "import this"'

Install NumPy and display its configuration::

    racker --verbose run --rm --platform=windows/amd64 python:3.10 -- 'sh -c "pip install numpy; python -c \"import numpy; numpy.show_config()\""'


Java
====

Display Java version, launched within containers in different environments::

    # Eclipse Temurin.
    racker --verbose run --rm --platform=windows/amd64 eclipse-temurin:16-jdk -- java --version
    racker --verbose run --rm --platform=windows/amd64 eclipse-temurin:18-jdk -- java --version

    # Oracle OpenJDK.
    racker --verbose run --rm --platform=windows/amd64 openjdk:8 -- java -version
    racker --verbose run --rm --platform=windows/amd64 openjdk:8-windowsservercore-ltsc2016 -- java -version
    racker --verbose run --rm --platform=windows/amd64 openjdk:8-windowsservercore-1809 -- java -version
    racker --verbose run --rm --platform=windows/amd64 openjdk:19 -- java --version

    # Explicitly select `2019-box` as different host OS.
    # The default would be to automatically select `2022-box`.
    RACKER_WDM_MACHINE=2019-box racker --verbose run --rm --platform=windows/amd64 openjdk:19 -- java --version

    # Nano Server
    racker --verbose run --rm --platform=windows/amd64 openjdk:19-nanoserver -- java --version


Invoke a Java command prompt (JShell) with different Java and OS versions::

    racker --verbose run -it --rm --platform=windows/amd64 eclipse-temurin:18-jdk jshell
    racker --verbose run -it --rm --platform=windows/amd64 openjdk:8-windowsservercore-ltsc2016 jshell
    racker --verbose run -it --rm --platform=windows/amd64 openjdk:8-windowsservercore-1809 jshell
    racker --verbose run -it --rm --platform=windows/amd64 openjdk:19-windowsservercore-ltsc2022 jshell
    System.out.println("OS: " + System.getProperty("os.name") + ", version " + System.getProperty("os.version"))
    System.out.println("Java: " + System.getProperty("java.vendor") + ", version " + System.getProperty("java.version"))
    /exit



******************
Container handbook
******************

Inquire system information
==========================

On systems where ``wmic`` is installed::

    docker --context=2019-box run -it --rm mcr.microsoft.com/windows/servercore:ltsc2019 cmd
    wmic cpu get NumberOfCores
    wmic computersystem get TotalPhysicalMemory

On systems where PowerShell is installed::

    docker --context=2019-box run -it --rm mcr.microsoft.com/windows/servercore:ltsc2019 powershell
    Get-ComputerInfo


Manipulating ``PATH``
=====================

Display the content of the ``PATH`` environment variable::

    echo %PATH%
    (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path).Path

Set the content of the ``PATH`` environment variable::

    # Using `setx`.
    setx PATH "$env:path;$($env:SystemDrive)\Program Files\Git\bin" -m

    # Using PowerShell.
    [Environment]::SetEnvironmentVariable('Path', $env:Path + ';' + $($env:SystemDrive) + '\Program Files\Git\bin', 'Machine')



***********
Admin guide
***********


Terminate a container
=====================

You will experience situations where the invocation of programs will block your
terminal and you can't terminate the process using ``CTRL+C``. For example, try
to run ``wish.exe``.

In such situations, you might want to kill the container. It works like this::

    # Find the container id.
    docker --context=2022-box ps

    # Terminate or stop the container.
    docker --context=2022-box kill 08df5fc812f9
    docker --context=2022-box stop 08df5fc812f9


The Docker contexts
===================

Communication from the Docker CLI to the Docker daemons running on the WDM
machines is established through Docker contexts.

To list all active contexts, type::

    docker context list

To remove the contexts automatically established by WDM, type::

    docker context rm 2016-box 2019-box 2022-box


Installing and using Chocolatey
===============================

The `Chocolatey`_ package manager can be used to install additional software like
``git`` and ``bash``::

    racker run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019 powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    choco install --yes git --package-parameters="/GitAndUnixToolsOnPath /Editor:Nano"
    iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/badrelmers/RefrEnv/main/refrenv.ps1'))

    $ bash --version
    $ git --version

The whole software catalog can be inquired at `Chocolatey community packages`_.


.. _Chocolatey: https://chocolatey.org/
.. _Chocolatey community packages: https://community.chocolatey.org/packages
.. _eclipse-temurin: https://hub.docker.com/_/eclipse-temurin
.. _Midnight Commander: https://en.wikipedia.org/wiki/Midnight_Commander
.. _Overview of System Center release options: https://docs.microsoft.com/en-us/system-center/ltsc-and-sac-overview
.. _Python: https://www.python.org/
.. _Using Racker and Postroj for CrateDB CI: https://github.com/cicerops/racker/blob/main/doc/cratedb.rst
.. _Vagrant: https://www.vagrantup.com/
.. _VirtualBox: https://www.virtualbox.org/
.. _Windows Container Base Images: https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-containers/container-base-images
.. _Windows container version compatibility: https://docs.microsoft.com/en-us/virtualization/windowscontainers/deploy-containers/version-compatibility
.. _Windows Docker Machine: https://github.com/StefanScherer/windows-docker-machine
.. _Winfetch: https://github.com/kiedtl/winfetch
.. _Wheels for Windows: https://github.com/PyTables/PyTables/pull/872#issuecomment-773535041
