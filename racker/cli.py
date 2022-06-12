# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import io
import logging
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout

import click

from postroj.api import pull_curated_image
from postroj.container import PostrojContainer
from postroj.exceptions import ProvisioningError, InvalidImageReference
from postroj.util import boot, subprocess_get_error_message
from postroj.winrunner import WinRunner
from racker.image import ImageLibrary

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(package_name="racker")
@click.option("--verbose", is_flag=True, required=False)
@click.option("--debug", is_flag=True, required=False)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot(ctx, verbose, debug)


@click.command()
@click.argument("name", type=str, required=True)
@click.pass_context
def racker_pull(ctx, name: str):
    """
    Pull rootfs images from suitable locations.

    hello-world
    redis
    library/redis
    docker.io/library/redis
    ghcr.io/jpmens/mqttwarn-full:nightly
    """
    library = ImageLibrary()
    library.acquire(name)


@click.command()
@click.option("--interactive", "-i", is_flag=True)
@click.option("--tty", "-t", is_flag=True)
@click.option("--rm", is_flag=True)
@click.option("--platform", type=str, required=False)
@click.argument("image", type=str, required=False)
@click.argument("command", nargs=-1, type=str)
@click.pass_context
def racker_run(ctx, interactive: bool, tty: bool, rm: bool, platform: str, image: str, command: str):
    """
    Spawn a container and run a command on it.
    Aims to be compatible with `docker run`.
    """

    """
    Goal
    ====

    Translate between those invocations and fill the gaps::

        docker run -it --rm debian:bullseye-slim bash
        systemd-run --machine=debian-bullseye --pty bash

    Progress
    ========
    ::

        # Works
        racker run -it --rm debian-bullseye bash
        # TODO: Advanced image resolution
        racker run -it --rm debian:bullseye-slim bash
    """

    verbose = ctx.parent.params.get("verbose", False)
    debug = ctx.parent.params.get("debug", False)

    # Adjust command line arguments and options.
    command = " ".join(command)
    use_pty = False
    if interactive or tty:
        use_pty = True

    # Use a different subsystem for running Windows containers on Linux or
    # macOS.
    if platform is None:
        pass

    elif platform == "windows/amd64":
        logger.info(f"Preparing runtime environment for platform {platform} and image {image}")
        try:
            runner = WinRunner(image=image)
        except InvalidImageReference as ex:
            raise SystemExit(ex.returncode)
        try:
            with redirect_stdout(sys.stderr):
                with redirect_stderr(sys.stderr):
                    runner.setup()
                    runner.start()
        except subprocess.CalledProcessError as ex:
            message = subprocess_get_error_message(exception=ex)
            logger.critical(f"Launching container failed. {message}")
            # subprocess_forward_stderr_stdout(exception=ex)
            raise SystemExit(ex.returncode)

        logger.info(f"Invoking command '{command}' on {image}")
        try:
            runner.run(command, interactive=interactive, tty=tty)
        except subprocess.CalledProcessError as ex:
            message = subprocess_get_error_message(exception=ex)
            logger.critical(f"Running command in Windows container on image {image} failed. {message}")
            raise SystemExit(ex.returncode)
        return

    else:
        raise NotImplementedError(f'Runtime for platform "{platform}" not supported yet')

    if sys.platform != "linux":
        raise NotImplementedError(f"Unable to launch Linux systems on non-Linux machines yet, "
                                  f"please use the Vagrant setup")

    # Acquire filesystem image.
    # TODO: Add more advanced image registry, maybe using `docker-py`,
    #       resolving image names from postroj-internal images, Docker Hub,
    #       GHCR, etc.
    try:
        rootfs = None
        try:
            rootfs = pull_curated_image(image)
        except ValueError as ex:
            if "Unknown image label" not in str(ex):
                raise

        if rootfs is None:
            library = ImageLibrary()
            rootfs = library.acquire(image)

    except subprocess.CalledProcessError as ex:
        message = subprocess_get_error_message(exception=ex)
        logger.critical(f"Acquiring filesystem image failed. {message}")
        # subprocess_forward_stderr_stdout(exception=ex)
        raise SystemExit(ex.returncode)

    except ProvisioningError as ex:
        raise SystemExit(1)

    # Status reporting.
    logger.info(f"Invoking command '{command}' on {rootfs}")

    # TODO: Combine verbose + capturing by employing some Tee-like multiplexing.
    # TODO: After killing most of the code in `util.cmd`, this might be able to go away as well?
    if debug:
        stdout = sys.stderr
        stderr = sys.stderr
    else:
        stdout = io.StringIO()
        stderr = io.StringIO()

    # Boot container and run command.
    with PostrojContainer(image_path=rootfs) as pc:
        try:
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    pc.boot()
                    pc.wait()

        except subprocess.CalledProcessError as ex:
            message = subprocess_get_error_message(exception=ex)
            logger.critical(f"Launching container failed. {message}")
            # subprocess_forward_stderr_stdout(exception=ex)
            raise SystemExit(ex.returncode)

        try:
            pc.run(command, use_pty=use_pty)
        except subprocess.CalledProcessError as ex:
            message = subprocess_get_error_message(exception=ex)
            logger.critical(f"Running command in container '{pc.machine}' failed. {message}")
            raise SystemExit(ex.returncode)


cli.add_command(cmd=racker_pull, name="pull")
cli.add_command(cmd=racker_run, name="run")
