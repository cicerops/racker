#!/bin/bash
#
# Build wheels for PyTables on Windows. DIY, without a hosted CI provider.
# https://github.com/cicerops/racker/blob/main/doc/use-cases/python-on-windows.rst
#
# Synopsis::
#
#   racker --verbose run -it --rm --platform=windows/amd64 python:3.9 -- bash
#   /c/racker/doc/use-cases/windows-pytables-wheel.sh
#
set -e

# Install prerequisites.

# Microsoft Visual C++ Build Tools 2015 14.0.25420.1
# https://community.chocolatey.org/packages/microsoft-visual-cpp-build-tools
choco install --yes microsoft-visual-cpp-build-tools --install-arguments="'/InstallSelectableItems Win81SDK_CppBuildSKUV1;VisualCppBuildTools_ATLMFC_SDK'"

# Miniconda - A minimal installer for Anaconda.
# https://conda.io/miniconda.html
# https://community.chocolatey.org/packages/miniconda3
choco install --yes miniconda3 --package-parameters="'/AddToPath:1'"
export PATH="$PATH:/c/Tools/miniconda3/condabin"
export conda="conda.bat"

# cibuildwheel - Build Python wheels for all the platforms on CI with minimal configuration.
# https://cibuildwheel.readthedocs.io/
pip install --upgrade cibuildwheel

# Check prerequisites.
echo $PATH
$conda --version
# cibuildwheel --version


# Acquire sources.
mkdir -p /c/src
cd /c/src
test ! -d PyTables && git clone https://github.com/PyTables/PyTables --recursive --depth=1
cd PyTables

# Pretend to be on a build matrix.
export MATRIX_ARCH=win_amd64      # win32
export MATRIX_ARCH_SUBDIR=win-64  # win-32


# Configure cibuildwheel.
export CIBW_BUILD="cp36-${MATRIX_ARCH} cp37-${MATRIX_ARCH} cp38-${MATRIX_ARCH} cp39-${MATRIX_ARCH} cp310-${MATRIX_ARCH}"
export CIBW_BEFORE_ALL_WINDOWS="$conda create --yes --name=build && $conda activate build && $conda config --env --set subdir ${MATRIX_ARCH_SUBDIR} && $conda install --yes blosc bzip2 hdf5 lz4 lzo snappy zstd zlib"
export CIBW_ENVIRONMENT_WINDOWS='CONDA_PREFIX="C:\\Miniconda\\envs\\build" PATH="$PATH;C:\\Miniconda\\envs\\build\\Library\\bin"'
export CIBW_ENVIRONMENT="PYTABLES_NO_EMBEDDED_LIBS=true DISABLE_AVX2=true"
export CIBW_BEFORE_BUILD="pip install -r requirements.txt cython>=0.29.21 delvewheel"
export CIBW_REPAIR_WHEEL_COMMAND_WINDOWS="delvewheel repair -w {dest_dir} {wheel}"

# Debugging.
# env

# Build wheel.
cibuildwheel --platform=windows --output-dir=wheelhouse
