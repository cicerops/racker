# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import re
import shlex
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest
from click._compat import strip_ansi
from click.testing import CliRunner

from racker.cli import cli


# Currently, this test module effectively runs well on Linux,
# because it invokes machinery based on `systemd-nspawn`.

if sys.platform != "linux":
    pytest.skip("Skipping Linux-only tests", allow_module_level=True)


def test_run_image_invalid(caplog):
    """
    Spawning a container with an invalid image label should fail.
    """
    runner = CliRunner()

    runner.invoke(cli, "run -it --rm foo true", catch_exceptions=False)
    assert "Acquiring filesystem image failed" in caplog.text
    # assert "Error reading manifest latest in docker.io/library/foo" in caplog.text


def test_run_command_docker_image_success(capfd, delay):
    """
    Spawn a Debian 9 "stretch" container and run `hostnamectl` on it.
    The container image will be acquired from Docker.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian:stretch-slim /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    captured = capfd.readouterr()

    assert "Static hostname: debuerreotype" in captured.out
    assert "Virtualization: systemd-nspawn" in captured.out
    assert "Operating System: Debian GNU/Linux 9 (stretch)" in captured.out
    assert captured.err == ""


def test_run_command_curated_cloudimage_success(capfd, delay):
    """
    Spawn an Ubuntu 22 "jammy" container and run `hostnamectl` on it.
    The container image will be derived from the upstream cloud image tarball.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm ubuntu-jammy /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    captured = capfd.readouterr()

    assert "Static hostname: ubuntu" in captured.out
    assert "Virtualization: systemd-nspawn" in captured.out
    assert "Operating System: Ubuntu 22.04 LTS" in captured.out
    assert captured.err == ""


def test_run_command_failure_path_not_absolute(capfd, delay):
    """
    Running an invalid command on a container should croak.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian:stretch-slim foo", catch_exceptions=False)
    assert result.exit_code == 1

    captured = capfd.readouterr()

    output = strip_ansi(captured.err).strip()
    assert output == "Failed to start transient service unit: Path foo is not absolute."


def test_run_command_failure_command_not_found(caplog, delay):
    """
    Running an invalid command on a container should croak.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian:stretch-slim /bin/foo", catch_exceptions=False)
    assert result.exit_code == 203

    assert "Running command in container" in caplog.text
    assert "Reason: /bin/foo: No such file or directory" in caplog.text


def test_run_stdin_stdout(monkeypatch, capsys, delay):
    """
    Spawn a container and write something to its stdin.
    Proof that echoing this to stdout again works well.
    """
    program_path = Path(sys.argv[0]).parent
    racker = program_path / "racker"
    command = f"{racker} run -it --rm debian:stretch-slim /bin/cat /dev/stdin"
    process = subprocess.run(shlex.split(command), input=b"foo", stdout=subprocess.PIPE, env={"TESTING": "true"})
    process.check_returncode()
    assert process.stdout == b"foo"


@pytest.mark.xfail(reason="Not working within Linux VM on macOS. Reason: "
                          "Cannot enable nested VT-x/AMD-V without nested-paging and unrestricted guest execution!")
def test_run_windows_valid_image(capfd, delay):
    """
    Request a valid Windows container image.

    Note: This is currently not possible, because somehow VT-x does not work
          well enough to support this scenario, at least not on macOS Catalina.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run --rm --platform=windows/amd64 mcr.microsoft.com/windows/nanoserver:ltsc2022 -- cmd /C ver", catch_exceptions=False)
    assert result.exit_code == 0

    captured = capfd.readouterr()
    assert "Microsoft Windows [Version 10.0.20348.707]" in captured.out


def test_run_windows_invalid_image(caplog, delay):
    """
    Request an invalid Windows container image and make sure it croaks correctly.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run --rm --platform=windows/amd64 images.example.org/foo/bar:special -- cmd /C ver", catch_exceptions=False)
    assert result.exit_code == 1

    assert re.match(".*Inquiring information about OCI image .+ failed.*", caplog.text)
    assert re.match(".*Reason:.*Error parsing image name .* (error )?pinging (container|docker) registry images.example.org.*", caplog.text)


def test_run_windows_mocked_noninteractive():
    """
    Pretend to launch a Windows container, but don't.
    Reason: The `WinRunner` machinery has been mocked completely.
    """
    runner = CliRunner()

    with mock.patch("racker.cli.WinRunner") as winrunner:
        result = runner.invoke(cli, "run --rm --platform=windows/amd64 images.example.org/foo/bar:special -- cmd /C ver", catch_exceptions=False)
    assert result.exit_code == 0
    assert winrunner.mock_calls == [
        mock.call(image='images.example.org/foo/bar:special'),
        mock.call().setup(),
        mock.call().start(),
        mock.call().run('cmd /C ver', interactive=False, tty=False),
    ]


def test_run_windows_mocked_interactive():
    """
    Pretend to launch a Windows container, but don't.
    Reason: The `WinRunner` machinery has been mocked completely.
    """
    runner = CliRunner()

    with mock.patch("racker.cli.WinRunner") as winrunner:
        result = runner.invoke(cli, "run -it --rm --platform=windows/amd64 images.example.org/foo/bar:special -- cmd /C ver", catch_exceptions=False)
    assert result.exit_code == 0
    assert winrunner.mock_calls == [
        mock.call(image='images.example.org/foo/bar:special'),
        mock.call().setup(),
        mock.call().start(),
        mock.call().run('cmd /C ver', interactive=True, tty=True),
    ]


# Unfortunately, this fails.
"""
def test_run_stdin_stdout_original(capfd):
    runner = CliRunner()

    sys.stdin = io.BytesIO(b"foo")
    result = runner.invoke(cli, "run -it --rm debian:stretch-slim /bin/cat /dev/stdin", input=b"foo", catch_exceptions=False)
    assert result.exit_code == 0

    # FIXME: Why is stdout empty?
    assert result.stdout == ""

    captured = capfd.readouterr()
    assert captured.out == "foo"
"""


# TODO: Provoke `Directory tree /var/lib/testdrive/postroj/archive/debian-stretch-slim.img/rootfs is currently busy.`, by
#       a) running a command while the container is still running.
#       b) trying to start a container twice.
