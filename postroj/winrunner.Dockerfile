# Windows runner Dockerfile for Racker
# https://github.com/cicerops/racker
#
# Provision a Windows operating system image.
#
# - Install the FOSS version of the Chocolatey package manager.
# - Install additional software using Chocolatey.
#

ARG BASE_IMAGE

FROM ${BASE_IMAGE}

# Install the Chocolatey package manager.
RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install essential and convenience programs.
RUN choco install --yes busybox curl nano wget
RUN choco install --yes git --package-parameters="'/GitAndUnixToolsOnPath /Editor:Nano'"

# Rename Windows-native programs in favor of Chocolatey-installed/FOSS/GNU ones.
# An alternative would be to manipulate `$PATH`, but that is more tedious.
RUN sh -c 'test -f /c/Windows/system32/curl && mv /c/Windows/system32/curl /c/Windows/system32/curl-win'
RUN sh -c 'test -f /c/Windows/system32/convert && mv /c/Windows/system32/convert /c/Windows/system32/convert-ntfs'
