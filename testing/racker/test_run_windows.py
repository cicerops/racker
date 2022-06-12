# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import os
import subprocess
import sys
from pathlib import Path
import shlex
import socket
from subprocess import CalledProcessError, CompletedProcess

import pytest


# Currently, this test module effectively runs well on macOS.
# The following snippet skips invocation on both VirtualBox
# and GitHub Actions.

if "rackerhost-debian11" in socket.gethostname():
    pytest.skip("Nested virtualization with VT-x fails within "
                "VirtualBox environment on developer's macOS workstation", allow_module_level=True)

if "GITHUB_ACTIONS" in os.environ:
    pytest.skip("Installing the Vagrant filesystem image for Windows "
                "takes too much disk space on GitHub Actions", allow_module_level=True)


def run_racker(command: str) -> subprocess.CompletedProcess:
    program_path = Path(sys.argv[0]).parent
    racker = program_path / "racker"
    command = f"{racker} {command}"
    process = subprocess.run(shlex.split(command), stdout=subprocess.PIPE)
    process.check_returncode()
    return process


def test_run_windows_cmd_success():
    """
    Launch a Windows Nanoserver container and invoke a `cmd` command.
    """
    process = run_racker("--verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:1809-amd64 cmd /C 'echo Hello, world.'")
    process.check_returncode()
    assert process.stdout == b"Hello, world.\r\n"


def test_run_windows_cmd_failure():
    """
    Check exit code propagation of a failing `cmd` command.
    """
    with pytest.raises(CalledProcessError) as ex:
        run_racker("--verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:1809-amd64 cmd /C 'exit 66'")
    process: CompletedProcess = ex.value
    assert process.returncode == 66


def test_run_windows_powershell_success():
    """
    Launch a Windows Server Core container and invoke a PowerShell command.
    """
    process = run_racker("--verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019-amd64 -- 'powershell -Command {echo \"Hello, world.\"}'")
    process.check_returncode()
    # FIXME: Why does `echo` get echoed here!?
    assert process.stdout == b"echo Hello, world.\r\n"


def test_run_windows_powershell_failure():
    """
    Check exit code propagation of a failing PowerShell command.
    """
    with pytest.raises(CalledProcessError) as ex:
        run_racker("--verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019-amd64 -- 'powershell -Command exit 66'")
    process: CompletedProcess = ex.value
    assert process.returncode == 66


def test_run_windows_bash_success():
    """
    Launch a Windows Server Core container and invoke a Bash command.
    """
    process = run_racker("--verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019-amd64 -- 'sh -c \"echo Hello, world.\"'")
    process.check_returncode()
    assert process.stdout == b"Hello, world.\n"


def test_run_windows_bash_failure():
    """
    Check exit code propagation of a failing Bash command.
    """
    with pytest.raises(CalledProcessError) as ex:
        run_racker("--verbose run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019-amd64 -- 'sh -c \"exit 66\"'")
    process: CompletedProcess = ex.value
    assert process.returncode == 66
