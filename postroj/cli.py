# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json

import click

from postroj import pkgprobe, selftest
from postroj.api import pull_multiple_images, pull_single_image
from postroj.registry import list_images
from postroj.util import boot


@click.group()
@click.version_option(package_name="racker")
@click.option("--verbose", is_flag=True, required=False)
@click.option("--debug", is_flag=True, required=False)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot(ctx, verbose, debug)


@click.command()
@click.pass_context
def cli_list_images(ctx: click.Context):
    """
    List all available filesystem images
    """
    print(json.dumps(list_images(), indent=2))


@click.command()
@click.argument("name", type=str, required=False)
@click.option("--all", "pull_all", is_flag=True, required=False)
@click.pass_context
def cli_pull(ctx: click.Context, name: str, pull_all: bool = False):
    """
    Pull curated rootfs images from suitable locations.
    """
    if not name and not pull_all:
        raise click.BadOptionUsage(option_name="name", message="Need image name or `--all`")

    if pull_all:
        names = list_images()
        pull_multiple_images(names)
    else:
        pull_single_image(name)


cli.add_command(cmd=cli_list_images, name="list-images")
cli.add_command(cmd=cli_pull, name="pull")
cli.add_command(cmd=pkgprobe.main, name="pkgprobe")
cli.add_command(cmd=selftest.selftest_main, name="selftest")
