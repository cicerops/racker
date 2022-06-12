# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
"""
A convenience wrapper around Windows Docker Machine by Stefan Scherer.

https://github.com/StefanScherer/windows-docker-machine
"""
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import appdirs
import pkg_resources

from postroj.exceptions import InvalidImageReference
from postroj.util import port_is_up, cmd, fix_tty, subprocess_get_error_message

logger = logging.getLogger(__name__)


class WinRunner:

    VAGRANT_PROVIDER = os.environ.get("RACKER_WDM_PROVIDER", "virtualbox")
    VCPUS = os.environ.get("RACKER_WDM_VCPUS", 4)
    MEMORY = os.environ.get("RACKER_WDM_MEMORY", 4096)

    def __init__(self, image: str):
        self.image_base = image
        self.image_real = "racker-runtime/" + self.image_base.replace("/", "-")

        self.wdm_machine = None
        self.choose_wdm_machine()
        logger.info(f"Using WDM host machine {self.wdm_machine} for launching container image {self.image_base}")

        self.workdir = Path(appdirs.user_state_dir(appname="racker"))
        self.workdir.mkdir(exist_ok=True, parents=True)

        self.wdmdir = self.workdir / "windows-docker-machine"

    def setup(self):
        """
        Prepare virtual machine and adjust system resources.
        """
        if not self.wdmdir.exists():
            logger.info(f"Installing Windows Docker Machine into {self.wdmdir}")
            command = f"""
                cd '{self.workdir}'
                git clone https://github.com/cicerops/windows-docker-machine --branch racker
                cd windows-docker-machine
                sed -i 's/v.cpus = [0-9]\+/v.cpus = {self.VCPUS}/' Vagrantfile
                sed -i 's/v.memory = [0-9]\+/v.memory = {self.MEMORY}/' Vagrantfile
                sed -i 's/v.maxmemory = [0-9]\+/v.maxmemory = {self.MEMORY}/' Vagrantfile
            """
            hshell(command)
        else:
            logger.info(f"Windows Docker Machine already installed into {self.wdmdir}")

    def choose_wdm_machine(self):
        """
        Choose the right virtual machine based on the container image to launch.
        """

        image = self.image_base
        if not image.startswith("docker://"):
            image = f"docker://{image}"

        logger.info(f"Inquiring information about OCI image '{image}'")

        if "RACKER_WDM_MACHINE" in os.environ:
            self.wdm_machine = os.environ["RACKER_WDM_MACHINE"]
            return

        # TODO: Cache the response from `skopeo inspect` to avoid the 3-second speed bump.
        #       https://github.com/cicerops/racker/issues/6
        command = f"skopeo --override-os=windows inspect --config --raw {image}"
        try:
            process = cmd(command, capture=True)
        except subprocess.CalledProcessError as ex:
            message = subprocess_get_error_message(exception=ex)
            message = f"Inquiring information about OCI image '{image}' failed. {message}"
            logger.error(message)
            exception = InvalidImageReference(message)
            exception.returncode = ex.returncode
            raise exception

        image_info = json.loads(process.stdout)
        image_os_name = image_info["os"]
        image_os_version = image_info["os.version"]
        logger.info(f"Image inquiry said os={image_os_name}, version={image_os_version}")

        if image_os_name != "windows":
            raise ValueError(f"Container image {image} is not Windows, but {image_os_name} instead")

        # https://docs.microsoft.com/en-us/virtualization/windowscontainers/deploy-containers/version-compatibility
        os_version_box_map = {
            "10.0.14393": "2016-box",
            "10.0.16299": "2019-box",   # openjdk:8-windowsservercore-1709
            "10.0.17763": "2019-box",
            "10.0.19042": "2022-box",
            "10.0.20348": "2022-box",
        }

        for os_version, machine in os_version_box_map.items():
            if image_os_version.startswith(os_version):
                self.wdm_machine = machine

        if self.wdm_machine is None:
            raise ValueError(f"Unable to choose WDM host machine for container image {image}, matching OS version {image_os_version}. "
                             f"Please report this error to https://github.com/cicerops/racker/issues/new.")

    def start(self, provision=False):
        """
        Start the "Windows Docker Machine" virtual machine.

        - Launch a virtual machine using Vagrant.
        - Connect to Docker daemon on virtual machine.
        - Provision the operating system image with additional software.
        """

        if self.docker_context_online():
            logger.info("Docker context is online")
        else:
            logger.info("Docker context is offline, starting VirtualBox VM with Vagrant")
            # TODO: The `provision` option flag is not wired in any way yet.
            #       https://github.com/cicerops/racker/issues/7
            provision_option = ""
            if provision:
                provision_option = "--provision"
            cmd(f"vagrant up --provider={self.VAGRANT_PROVIDER} {provision_option} {self.wdm_machine}", cwd=self.wdmdir, use_stderr=True)

        logger.info("Pinging Docker context")
        if not self.docker_context_online():
            raise IOError(f"Unable to bring up Docker context {self.wdm_machine}")

        # Attention: This can run into 60 second timeouts.
        # TODO: Use ``with stopit.ThreadingTimeout(timeout) as to_ctx_mgr``.
        # TODO: Make timeout values configurable.
        # https://github.com/moby/moby/blob/0e04b514fb/integration-cli/docker_cli_run_test.go
        cmd(f"docker --context={self.wdm_machine} ps", capture=True)

        # Skip installing software using Chocolatey for specific Windows OS versions.
        # - Windows Nanoserver does not have PowerShell.
        # - Windows 2016 croaks like:
        #   `The command 'cmd /S /C choco install --yes ...' returned a non-zero code: 3221225785`
        if "nanoserver" in self.image_base or self.wdm_machine == "2016-box":
            self.image_real = self.image_base
        else:
            self.provision_image()

    def provision_image(self):
        """
        Provide an operating system image by building a Docker image using `winrunner.Dockerfile`.

        - Provision a Windows operating system image with additional software.
        - Automatically installs the open source version of the Chocolatey package manager.
        - By default, it automatically installs some programs like `busybox`, `curl`, `git`,
          `nano`, and `wget`.
        """

        logger.info(f"Provisioning Docker image for Windows environment based on {self.image_base}")
        dockerfile = pkg_resources.resource_filename("postroj", "winrunner.Dockerfile")
        tmpdir = tempfile.mkdtemp()
        command = f"docker --context={self.wdm_machine} build --platform=windows/amd64 " \
                  f"--file={dockerfile} --build-arg=BASE_IMAGE={self.image_base} --tag={self.image_real} {tmpdir}"
        logger.debug(f"Running command: {command}")
        try:
            hcmd(command)
        except subprocess.CalledProcessError:
            raise
        finally:
            os.rmdir(tmpdir)

    def cmd(self, command):
        command = f"cmd /C {command}"
        return self.run(command)

    def powershell(self, command):
        command = f"powershell -Command {command}"
        return self.run(command)

    def run(self, command, interactive: bool = False, tty: bool = False):
        logger.info(f"Running guest command: {command}")

        option_interactive = ""
        if interactive or tty:
            option_interactive = "-it"

        # TODO: Propagate ``--rm`` option appropriately.
        # TODO: Propagate ``--volume`` option.
        #       option_volume = "--volume=C:/Users/amo/dev/cicerops-foss/sources/postroj:C:/racker"
        #       https://github.com/cicerops/racker/issues/8
        option_volume = ""
        command = f"docker --context={self.wdm_machine} run {option_interactive} --rm {option_volume} {self.image_real} {command}"

        # When an interactive prompt is requested, spawn a shell without further ado.
        if interactive or tty:
            ccmd(command, use_pty=True)

        # Otherwise, capture stdout and mangle its output.
        else:
            outcome = cmd(command)
            return outcome

    def docker_context_online(self):
        """
        Test if the Docker context is online.
        """
        logger.info(f"Checking connectivity to Docker daemon in Windows context '{self.wdm_machine}'")
        try:
            response = cmd(f"docker context inspect {self.wdm_machine}", capture=True)
        except:
            logger.warning(f"Docker context {self.wdm_machine} not online or not created yet")
            return False

        data = json.loads(response.stdout)
        address = urlparse(data[0]["Endpoints"]["docker"]["Host"])

        logger.info(f"Checking TCP connectivity to {address.hostname}:{address.port}")
        return port_is_up(address.hostname, address.port)


def hcmd(command, cwd=None,  use_stderr=True, silent=False):
    logger.debug(f"Running command: {command}")
    return cmd(command, cwd=cwd, use_stderr=use_stderr)


def hshell(command, cwd=None):
    logger.debug(f"Running command: {command}")
    #return cmd(command, cwd=cwd, passthrough=True).stdout
    return subprocess.check_output(command, shell=True, cwd=cwd).decode()


def ccmd(command, use_pty=False, capture=False):
    logger.debug(f"Running command: {command}")
    p = cmd(command=command, use_pty=use_pty, capture=capture)
    stdout = p.stdout
    if use_pty:
        fix_tty()
    return stdout
