# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import pytest

from postroj.winrunner import ccmd, hshell, hcmd


def test_hcmd_echo_newline(capfd):
    process = hcmd("/bin/echo foo", use_stderr=False)
    assert process.stdout is None
    assert process.stderr is None

    result = capfd.readouterr()
    assert result.out == "foo\n"
    assert result.err == ""


def test_hcmd_echo_no_newline(capfd):
    hcmd("/bin/echo -n foo", use_stderr=False)
    result = capfd.readouterr()
    assert result.out == "foo"


def test_hshell_echo_newline():
    output = hshell("/bin/echo foo")
    assert output == "foo\n"


def test_hshell_echo_no_newline():
    output = hshell("/bin/echo -n foo")
    assert output == "foo"


def test_ccmd_echo_newline():
    output = ccmd("/bin/echo foo", capture=True)
    assert output == "foo\n"


def test_ccmd_echo_newline_pty(capfd):
    output = ccmd("/bin/echo foo", capture=True, use_pty=True)
    assert output is None

    result = capfd.readouterr()
    assert result.out == "foo\n"
    assert result.err == ""


@pytest.mark.xfail
def test_ccmd_echo_no_newline():
    output = ccmd("/bin/echo -n foo", capture=True)
    assert output == "foo"


def test_ccmd_echo_no_newline_pty(capfd):
    output = ccmd("/bin/echo -n foo", capture=True, use_pty=True)
    assert output is None

    result = capfd.readouterr()
    assert result.out == "foo"
    assert result.err == ""
